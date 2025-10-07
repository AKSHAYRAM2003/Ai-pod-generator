"""
Regenerate missing thumbnails for podcasts
"""
import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import AsyncSessionLocal
from app.models.podcast import Podcast
from app.services.thumbnail_service import ThumbnailService
from app.services.storage_service import StorageService

async def regenerate_missing_thumbnails():
    async with AsyncSessionLocal() as db:
        # Get all podcasts without thumbnails
        result = await db.execute(
            select(Podcast)
            .options(selectinload(Podcast.category))
            .where(
                (Podcast.thumbnail_url == None) | (Podcast.thumbnail_url == "")
            ).order_by(Podcast.created_at.desc())
        )
        podcasts = result.scalars().all()
        
        print(f"\n{'='*80}")
        print(f"REGENERATING THUMBNAILS FOR {len(podcasts)} PODCASTS")
        print(f"{'='*80}\n")
        
        thumbnail_service = ThumbnailService()
        storage_service = StorageService()
        
        for i, podcast in enumerate(podcasts, 1):
            print(f"{i}. Processing: {podcast.title}")
            print(f"   ID: {podcast.id}")
            print(f"   User ID: {podcast.user_id}")
            
            try:
                # Get category name if available
                category_name = None
                if podcast.category:
                    category_name = podcast.category.name
                
                # Generate thumbnail using sync method
                print(f"   Generating thumbnail...")
                thumbnail_data = thumbnail_service.generate_thumbnail_sync(
                    topic=podcast.topic or podcast.title,
                    description=podcast.description or f"A podcast about {podcast.topic or podcast.title}",
                    category_name=category_name
                )
                
                if thumbnail_data:
                    print(f"   Thumbnail generated ({len(thumbnail_data)} bytes)")
                    
                    # Save thumbnail
                    print(f"   Saving thumbnail...")
                    thumbnail_path = await storage_service.save_thumbnail(
                        user_id=podcast.user_id,
                        podcast_id=str(podcast.id),
                        thumbnail_data=thumbnail_data
                    )
                    
                    # Update podcast
                    podcast.thumbnail_url = thumbnail_path
                    await db.commit()
                    
                    print(f"   ✓ Success! Thumbnail saved to: {thumbnail_path}")
                else:
                    print(f"   ✗ Failed to generate thumbnail")
                    
            except Exception as e:
                print(f"   ✗ Error: {str(e)}")
                await db.rollback()
            
            print()
        
        print(f"{'='*80}")
        print(f"REGENERATION COMPLETE")
        print(f"{'='*80}\n")

if __name__ == "__main__":
    asyncio.run(regenerate_missing_thumbnails())
