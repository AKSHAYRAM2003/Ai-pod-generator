"""
Generate thumbnails for existing podcasts
Run this script to add AI-generated thumbnails to podcasts that don't have them
"""
import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.podcast import Podcast, PodcastStatus
from app.services.thumbnail_service import thumbnail_service
from app.services.storage_service import storage_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_thumbnails_for_existing_podcasts():
    """Generate thumbnails for all completed podcasts without thumbnails"""
    
    async with AsyncSessionLocal() as session:
        try:
            # Get all completed podcasts without thumbnails
            result = await session.execute(
                select(Podcast).where(
                    Podcast.status == PodcastStatus.COMPLETED,
                    Podcast.thumbnail_url.is_(None)
                ).options(
                    selectinload(Podcast.category)
                )
            )
            podcasts = result.scalars().all()
            
            # Force load all attributes
            for podcast in podcasts:
                _ = podcast.topic
                _ = podcast.description
                if podcast.category:
                    _ = podcast.category.name
            
            logger.info(f"Found {len(podcasts)} podcasts without thumbnails")
            
            if not podcasts:
                logger.info("No podcasts need thumbnails. Exiting.")
                return
            
            # Process each podcast
            for index, podcast in enumerate(podcasts, 1):
                logger.info(f"\n[{index}/{len(podcasts)}] Processing podcast: {podcast.topic}")
                
                try:
                    # Get category name
                    category_name = None
                    if podcast.category:
                        category_name = podcast.category.name
                    
                    # Generate thumbnail
                    logger.info(f"Generating thumbnail...")
                    thumbnail_data = await thumbnail_service.generate_thumbnail(
                        topic=podcast.topic,
                        description=podcast.description,
                        category_name=category_name,
                    )
                    
                    # Save thumbnail
                    logger.info(f"Saving thumbnail...")
                    thumbnail_url = await storage_service.save_thumbnail(
                        image_data=thumbnail_data,
                        podcast_id=str(podcast.id),
                        user_id=podcast.user_id,
                        format="png"
                    )
                    
                    # Update podcast
                    podcast.thumbnail_url = thumbnail_url
                    await session.commit()
                    
                    logger.info(f"✅ Thumbnail generated and saved: {thumbnail_url}")
                    
                    # Small delay to avoid rate limiting
                    if index < len(podcasts):
                        await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing podcast {podcast.id}: {e}")
                    await session.rollback()
                    continue
            
            logger.info(f"\n✅ Completed! Processed {len(podcasts)} podcasts")
            
        except Exception as e:
            logger.error(f"Error in thumbnail generation: {e}")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("  GENERATING THUMBNAILS FOR EXISTING PODCASTS")
    print("=" * 60)
    print()
    
    asyncio.run(generate_thumbnails_for_existing_podcasts())
    
    print()
    print("=" * 60)
    print("  THUMBNAIL GENERATION COMPLETE")
    print("=" * 60)
