from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.podcast import Podcast, PodcastStatus as PodcastStatusEnum
from app.models.category import Category
from app.schemas.podcast import (
    PodcastCreateRequest,
    PodcastResponse,
    PodcastListResponse,
    PodcastStatusResponse,
    PodcastPublishRequest,
    CategoryResponse
)
from app.tasks.podcast_tasks import generate_podcast_task

router = APIRouter(prefix="/podcasts", tags=["podcasts"])


# Rate limiting constants
RATE_LIMIT_WINDOW = timedelta(hours=24)
MAX_PODCASTS_PER_DAY = 5


async def check_rate_limit(user_id: int, db: AsyncSession):
    """Check if user has exceeded podcast generation rate limit"""
    # Premium user - unlimited podcasts
    PREMIUM_USER_ID = 14  # akshayram244@gmail.com
    if user_id == PREMIUM_USER_ID:
        logger.info(f"Premium user {user_id} - skipping rate limit")
        return
    
    time_threshold = datetime.utcnow() - RATE_LIMIT_WINDOW
    
    result = await db.execute(
        select(func.count()).select_from(Podcast).filter(
            Podcast.user_id == user_id,
            Podcast.created_at >= time_threshold
        )
    )
    podcast_count = result.scalar()
    
    if podcast_count >= MAX_PODCASTS_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. You can generate up to {MAX_PODCASTS_PER_DAY} podcasts per 24 hours."
        )


@router.post("/", response_model=PodcastResponse, status_code=status.HTTP_201_CREATED)
async def create_podcast(
    request: PodcastCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new podcast generation request.
    
    - Validates input parameters
    - Checks rate limiting
    - Creates podcast record
    - Queues background task for generation
    """
    # Check rate limit
    await check_rate_limit(current_user.id, db)
    
    # Validate category exists
    result = await db.execute(select(Category).filter(Category.id == request.category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Validate duration is one of allowed values
    if request.duration not in [5, 7, 10]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duration must be 5, 7, or 10 minutes"
        )
    
    # Validate speaker mode requirements
    if request.speaker_mode == "single" and not request.voice_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="voice_type is required for single speaker mode"
        )
    
    if request.speaker_mode == "two" and not request.conversation_style:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="conversation_style is required for two speaker mode"
        )
    
    # Create podcast record
    # Generate title from topic (will be updated with AI-generated title later)
    title = request.topic[:100] if len(request.topic) <= 100 else request.topic[:97] + "..."
    description = f"An AI-generated podcast about {request.topic}"
    
    podcast = Podcast(
        user_id=current_user.id,
        category_id=request.category_id,
        topic=request.topic,
        title=title,
        description=description,
        duration=request.duration,
        speaker_mode=request.speaker_mode,
        voice_type=request.voice_type,
        conversation_style=request.conversation_style,
        status=PodcastStatusEnum.DRAFT,
        is_public=False
    )
    
    db.add(podcast)
    await db.commit()
    await db.refresh(podcast)
    
    # Queue background task or run directly
    # Queue background task with Celery
    try:
        task = generate_podcast_task.delay(str(podcast.id))
        logger.info(f"Queued podcast generation task {task.id} for podcast {podcast.id}")
    except Exception as e:
        # If Celery fails, mark as failed and return error
        logger.error(f"Failed to queue podcast generation task: {e}")
        podcast.status = PodcastStatusEnum.FAILED
        podcast.error_message = "Failed to queue generation task. Please ensure Celery worker is running."
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background task service unavailable. Please try again later."
        )
    
    # Reload podcast with category relationship
    result = await db.execute(
        select(Podcast).options(selectinload(Podcast.category))
        .filter(Podcast.id == podcast.id)
    )
    podcast = result.scalar_one()
    
    return podcast


@router.get("/my-podcasts", response_model=PodcastListResponse)
async def get_my_podcasts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    status_filter: Optional[PodcastStatusEnum] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's podcasts (both public and private).
    
    - Paginated results
    - Optional status filtering
    - Ordered by creation date (newest first)
    """
    # Build query
    query = select(Podcast).filter(Podcast.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Podcast.status == status_filter)
    
    # Get total count
    count_result = await db.execute(
        select(func.count()).select_from(Podcast).filter(Podcast.user_id == current_user.id)
    )
    total = count_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(desc(Podcast.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size)
    
    result = await db.execute(query)
    podcasts = result.scalars().all()
    
    # Load categories
    for podcast in podcasts:
        cat_result = await db.execute(select(Category).filter(Category.id == podcast.category_id))
        podcast.category = cat_result.scalar_one_or_none()
    
    total_pages = (total + page_size - 1) // page_size
    
    return PodcastListResponse(
        podcasts=podcasts,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/discover", response_model=PodcastListResponse)
async def discover_podcasts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get public podcasts for discovery page.
    
    - Only shows completed, public podcasts
    - Paginated results
    - Optional category filtering
    - Ordered by creation date (newest first)
    """
    # Build query
    query = select(Podcast).filter(
        Podcast.is_public == True,
        Podcast.status == PodcastStatusEnum.COMPLETED
    )
    
    if category_id:
        query = query.filter(Podcast.category_id == category_id)
    
    # Get total count
    count_query = select(func.count()).select_from(Podcast).filter(
        Podcast.is_public == True,
        Podcast.status == PodcastStatusEnum.COMPLETED
    )
    if category_id:
        count_query = count_query.filter(Podcast.category_id == category_id)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # Apply pagination
    query = query.order_by(desc(Podcast.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size)
    
    result = await db.execute(query)
    podcasts = result.scalars().all()
    
    # Load categories
    for podcast in podcasts:
        cat_result = await db.execute(select(Category).filter(Category.id == podcast.category_id))
        podcast.category = cat_result.scalar_one_or_none()
    
    total_pages = (total + page_size - 1) // page_size
    
    return PodcastListResponse(
        podcasts=podcasts,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{podcast_id}", response_model=PodcastResponse)
async def get_podcast(
    podcast_id: UUID,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific podcast by ID.
    
    - Public podcasts: accessible to anyone
    - Private podcasts: only accessible to owner
    """
    result = await db.execute(select(Podcast).filter(Podcast.id == podcast_id))
    podcast = result.scalar_one_or_none()
    
    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found"
        )
    
    # Check access permissions
    if not podcast.is_public:
        if not current_user or podcast.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this private podcast"
            )
    
    # Load category
    cat_result = await db.execute(select(Category).filter(Category.id == podcast.category_id))
    podcast.category = cat_result.scalar_one_or_none()
    
    return podcast


@router.get("/{podcast_id}/status", response_model=PodcastStatusResponse)
async def get_podcast_status(
    podcast_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the processing status of a podcast.
    
    - Returns current status, progress, and any error messages
    - Only accessible to podcast owner
    """
    result = await db.execute(
        select(Podcast).filter(
            Podcast.id == podcast_id,
            Podcast.user_id == current_user.id
        )
    )
    podcast = result.scalar_one_or_none()
    
    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found"
        )
    
    # Calculate progress percentage
    progress = None
    stage = None
    
    # Get progress from ai_metadata if available
    if podcast.ai_metadata and isinstance(podcast.ai_metadata, dict):
        progress = podcast.ai_metadata.get('progress')
        stage = podcast.ai_metadata.get('stage')
    
    # Fallback to status-based progress if metadata not available
    if progress is None:
        if podcast.status == PodcastStatusEnum.DRAFT:
            progress = 0
            stage = "Queued"
        elif podcast.status == PodcastStatusEnum.GENERATING:
            progress = 50
            stage = "Generating"
        elif podcast.status == PodcastStatusEnum.COMPLETED:
            progress = 100
            stage = "Completed"
        elif podcast.status == PodcastStatusEnum.FAILED:
            progress = 0
            stage = "Failed"
    
    return PodcastStatusResponse(
        id=podcast.id,
        status=podcast.status,
        progress=progress,
        stage=stage,
        audio_url=podcast.audio_url,
        error_message=podcast.error_message
    )


@router.patch("/{podcast_id}/publish", response_model=PodcastResponse)
async def publish_podcast(
    podcast_id: UUID,
    request: PodcastPublishRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Publish or unpublish a podcast.
    
    - Only completed podcasts can be published
    - Only owner can change publication status
    """
    result = await db.execute(
        select(Podcast).filter(
            Podcast.id == podcast_id,
            Podcast.user_id == current_user.id
        )
    )
    podcast = result.scalar_one_or_none()
    
    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found"
        )
    
    # Can only publish completed podcasts
    if request.is_public and podcast.status != PodcastStatusEnum.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed podcasts can be published"
        )
    
    podcast.is_public = request.is_public
    await db.commit()
    await db.refresh(podcast)
    
    # Load category
    cat_result = await db.execute(select(Category).filter(Category.id == podcast.category_id))
    podcast.category = cat_result.scalar_one_or_none()
    
    return podcast


@router.delete("/{podcast_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_podcast(
    podcast_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a podcast.
    
    - Only owner can delete
    - Deletes database record and audio file
    """
    result = await db.execute(
        select(Podcast).filter(
            Podcast.id == podcast_id,
            Podcast.user_id == current_user.id
        )
    )
    podcast = result.scalar_one_or_none()
    
    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found"
        )
    
    # Delete audio file if exists
    if podcast.audio_url:
        try:
            from app.services.storage_service import StorageService
            storage = StorageService()
            storage.delete_audio(podcast.audio_url)
        except Exception as e:
            # Log error but don't fail the delete operation
            print(f"Error deleting audio file: {e}")
    
    await db.delete(podcast)
    await db.commit()
    
    return None


@router.get("/categories/list", response_model=list[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    Get all available podcast categories.
    """
    result = await db.execute(select(Category).order_by(Category.name))
    categories = result.scalars().all()
    return categories
