"""
Storage Service
Handles file storage for podcast audio files
Supports both local filesystem and Google Cloud Storage
"""
import os
import uuid
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Storage configuration
STORAGE_MODE = os.getenv("STORAGE_MODE", "local")  # "local" or "gcs"
LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "storage/podcasts")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "aipod-podcasts-production")


class StorageService:
    """Service for storing and retrieving podcast audio files"""
    
    def __init__(self):
        self.mode = STORAGE_MODE
        self._ensure_local_storage()
    
    def _ensure_local_storage(self):
        """Ensure local storage directory exists"""
        if self.mode == "local":
            Path(LOCAL_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    
    async def save_audio(
        self,
        audio_data: bytes,
        podcast_id: str,
        user_id: int,
        format: str = "mp3"
    ) -> str:
        """
        Save audio file and return URL
        
        Args:
            audio_data: Audio file bytes
            podcast_id: Podcast UUID
            user_id: User ID
            format: Audio format (default: mp3)
            
        Returns:
            URL to access the audio file
        """
        try:
            if self.mode == "local":
                return await self._save_local(audio_data, podcast_id, user_id, format)
            else:
                return await self._save_gcs(audio_data, podcast_id, user_id, format)
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            raise
    
    async def save_thumbnail(
        self,
        image_data: bytes,
        podcast_id: str,
        user_id: int,
        format: str = "png"
    ) -> str:
        """
        Save thumbnail image and return URL
        
        Args:
            image_data: Image file bytes
            podcast_id: Podcast UUID
            user_id: User ID
            format: Image format (default: png)
            
        Returns:
            URL to access the thumbnail image
        """
        try:
            if self.mode == "local":
                return await self._save_thumbnail_local(image_data, podcast_id, user_id, format)
            else:
                return await self._save_thumbnail_gcs(image_data, podcast_id, user_id, format)
        except Exception as e:
            logger.error(f"Error saving thumbnail: {e}")
            raise
    
    async def _save_local(
        self,
        audio_data: bytes,
        podcast_id: str,
        user_id: int,
        format: str
    ) -> str:
        """Save audio to local filesystem"""
        try:
            # Create user directory
            user_dir = Path(LOCAL_STORAGE_PATH) / f"user_{user_id}" / str(podcast_id)
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = user_dir / f"audio.{format}"
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            
            # Return relative URL (will be served by FastAPI static files)
            url = f"/storage/podcasts/user_{user_id}/{podcast_id}/audio.{format}"
            logger.info(f"Saved audio locally: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Error saving to local storage: {e}")
            raise
    
    async def _save_thumbnail_local(
        self,
        image_data: bytes,
        podcast_id: str,
        user_id: int,
        format: str
    ) -> str:
        """Save thumbnail to local filesystem"""
        try:
            # Create user directory
            user_dir = Path(LOCAL_STORAGE_PATH) / f"user_{user_id}" / str(podcast_id)
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = user_dir / f"thumbnail.{format}"
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            # Return relative URL (will be served by FastAPI static files)
            url = f"/storage/podcasts/user_{user_id}/{podcast_id}/thumbnail.{format}"
            logger.info(f"Saved thumbnail locally: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Error saving thumbnail to local storage: {e}")
            raise
    
    async def _save_gcs(
        self,
        audio_data: bytes,
        podcast_id: str,
        user_id: int,
        format: str
    ) -> str:
        """Save audio to Google Cloud Storage"""
        try:
            # TODO: Implement GCS upload for production
            # from google.cloud import storage
            # client = storage.Client()
            # bucket = client.bucket(GCS_BUCKET_NAME)
            # blob = bucket.blob(f"users/{user_id}/{podcast_id}/audio.{format}")
            # blob.upload_from_string(audio_data, content_type=f"audio/{format}")
            # return blob.public_url
            
            # For now, fall back to local storage
            logger.warning("GCS not implemented, falling back to local storage")
            return await self._save_local(audio_data, podcast_id, user_id, format)
            
        except Exception as e:
            logger.error(f"Error saving to GCS: {e}")
            raise
    
    async def _save_thumbnail_gcs(
        self,
        image_data: bytes,
        podcast_id: str,
        user_id: int,
        format: str
    ) -> str:
        """Save thumbnail to Google Cloud Storage"""
        try:
            # TODO: Implement GCS upload for production
            # For now, fall back to local storage
            logger.warning("GCS thumbnail upload not implemented, falling back to local storage")
            return await self._save_thumbnail_local(image_data, podcast_id, user_id, format)
            
        except Exception as e:
            logger.error(f"Error saving thumbnail to GCS: {e}")
            raise
    
    async def delete_audio(self, audio_url: str) -> bool:
        """
        Delete audio file
        
        Args:
            audio_url: URL of the audio file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if self.mode == "local":
                return await self._delete_local(audio_url)
            else:
                return await self._delete_gcs(audio_url)
        except Exception as e:
            logger.error(f"Error deleting audio: {e}")
            return False
    
    async def _delete_local(self, audio_url: str) -> bool:
        """Delete audio from local filesystem"""
        try:
            # Convert URL to file path
            file_path = Path(audio_url.replace("/storage/podcasts/", LOCAL_STORAGE_PATH + "/"))
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted local audio: {audio_url}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting from local storage: {e}")
            return False
    
    async def _delete_gcs(self, audio_url: str) -> bool:
        """Delete audio from Google Cloud Storage"""
        try:
            # TODO: Implement GCS deletion for production
            logger.warning("GCS deletion not implemented")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting from GCS: {e}")
            return False


# Singleton instance
storage_service = StorageService()
