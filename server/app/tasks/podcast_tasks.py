"""
Podcast Generation Tasks
Celery tasks for asynchronous podcast generation
"""
import asyncio
import logging
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.podcast import Podcast, PodcastStatus
from app.services.gemini_podcast_service import gemini_service
from app.services.storage_service import storage_service
from app.utils.audio_utils import pcm_to_mp3, get_audio_duration

logger = logging.getLogger(__name__)

# Try to apply nest_asyncio for nested event loop support
# This is only needed when running Celery tasks
try:
    import nest_asyncio
    # Only apply if we're not using uvloop (which doesn't support nest_asyncio)
    try:
        loop = asyncio.get_event_loop()
        if 'uvloop' not in str(type(loop)):
            nest_asyncio.apply()
            logger.info("nest_asyncio applied successfully")
    except RuntimeError:
        # No event loop yet, will apply when needed
        pass
except ImportError:
    logger.warning("nest_asyncio not available")


@celery_app.task(bind=True, name="app.tasks.podcast_tasks.generate_podcast_task")
def generate_podcast_task(self, podcast_id: str):
    """
    Background task to generate podcast audio
    
    Args:
        podcast_id: UUID of the podcast to generate
    """
    logger.info(f"[Task {self.request.id}] Starting podcast generation for {podcast_id}")
    
    try:
        # Use asyncio.run() which creates a fresh event loop for this task
        # nest_asyncio allows this to work even if called from an async context
        asyncio.run(_generate_podcast_async(podcast_id, self.request.id))
        logger.info(f"[Task {self.request.id}] Podcast generation completed successfully")
        
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Podcast generation failed: {e}")
        # Update podcast status to failed
        try:
            asyncio.run(_mark_podcast_failed(podcast_id, str(e)))
        except Exception as mark_error:
            logger.error(f"[Task {self.request.id}] Error marking podcast as failed: {mark_error}")
        raise


async def _generate_podcast_async(podcast_id: str, task_id: str):
    """Async function to generate podcast"""
    async with AsyncSessionLocal() as session:
        try:
            # Get podcast from database
            result = await session.execute(
                select(Podcast).where(Podcast.id == UUID(podcast_id))
            )
            podcast = result.scalar_one_or_none()
            
            if not podcast:
                raise Exception(f"Podcast {podcast_id} not found")
            
            # Update status to GENERATING at the start
            podcast.status = PodcastStatus.GENERATING
            podcast.ai_metadata = {"progress": 5, "stage": "Initializing..."}
            await session.commit()
            
            logger.info(f"[Task {task_id}] Generating script for: {podcast.topic}")
            
            # Step 1: Generate script (10-40% progress)
            await _update_podcast_metadata(session, podcast, {"progress": 10, "stage": "Generating script..."})
            
            script = await gemini_service.generate_podcast_script(
                topic=podcast.topic,
                description=podcast.description,
                duration=podcast.duration,
                speaker_mode=podcast.speaker_mode,
                voice_type=podcast.voice_type,
                conversation_style=podcast.conversation_style,
            )
            
            # Save script
            podcast.script = script
            await session.commit()
            
            logger.info(f"[Task {task_id}] Script generated, now generating audio")
            
            # Step 2: Generate audio (40-80% progress)
            await _update_podcast_metadata(session, podcast, {"progress": 40, "stage": "Creating audio..."})
            
            audio_pcm = await gemini_service.generate_podcast_audio(
                script=script,
                speaker_mode=podcast.speaker_mode,
                voice_type=podcast.voice_type,
            )
            
            logger.info(f"[Task {task_id}] Audio generated, converting to MP3")
            
            # Step 3: Convert to MP3 (80-85% progress)
            await _update_podcast_metadata(session, podcast, {"progress": 80, "stage": "Converting to MP3..."})
            
            audio_mp3 = pcm_to_mp3(audio_pcm)
            
            # Step 4: Save audio file (85-95% progress)
            await _update_podcast_metadata(session, podcast, {"progress": 85, "stage": "Saving audio file..."})
            
            audio_url = await storage_service.save_audio(
                audio_data=audio_mp3,
                podcast_id=str(podcast.id),
                user_id=podcast.user_id,
                format="mp3"
            )
            
            # Get audio duration
            await _update_podcast_metadata(session, podcast, {"progress": 95, "stage": "Finalizing..."})
            duration_seconds = get_audio_duration(audio_mp3, format="mp3")
            
            # Step 5: Update podcast record (100% progress)
            podcast.audio_url = audio_url
            podcast.audio_duration = int(duration_seconds) if duration_seconds else None
            podcast.status = PodcastStatus.COMPLETED
            podcast.ai_metadata = {
                "progress": 100,
                "stage": "Completed",
                "task_id": task_id
            }
            
            await session.commit()
            
            logger.info(f"[Task {task_id}] Podcast generation complete: {audio_url}")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"[Task {task_id}] Error in podcast generation: {e}")
            raise


async def _update_podcast_metadata(session: AsyncSession, podcast: Podcast, metadata: dict):
    """Update podcast metadata (progress tracking)"""
    try:
        podcast.ai_metadata = metadata
        await session.commit()
    except Exception as e:
        logger.error(f"Error updating podcast metadata: {e}")


async def _mark_podcast_failed(podcast_id: str, error_message: str):
    """Mark podcast as failed"""
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(
                update(Podcast)
                .where(Podcast.id == UUID(podcast_id))
                .values(
                    status=PodcastStatus.FAILED,
                    error_message=error_message,
                    ai_metadata={"progress": 0, "stage": "Failed"}
                )
            )
            await session.commit()
            logger.info(f"Marked podcast {podcast_id} as failed")
        except Exception as e:
            logger.error(f"Error marking podcast as failed: {e}")
