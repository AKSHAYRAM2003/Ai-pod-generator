from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID


class SpeakerMode(str, Enum):
    SINGLE = "single"
    TWO = "two"


class VoiceType(str, Enum):
    MALE = "male"
    FEMALE = "female"


class ConversationStyle(str, Enum):
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    EDUCATIONAL = "educational"


class PodcastStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    PUBLISHED = "published"


class PodcastCreateRequest(BaseModel):
    """Request schema for creating a new podcast"""
    topic: str = Field(..., min_length=5, max_length=500, description="Podcast topic")
    category_id: UUID = Field(..., description="Category UUID")
    duration: int = Field(..., ge=5, le=10, description="Duration in minutes (5, 7, or 10)")
    speaker_mode: SpeakerMode = Field(..., description="Single or two-speaker mode")
    voice_type: Optional[VoiceType] = Field(None, description="Voice type for single speaker")
    conversation_style: Optional[ConversationStyle] = Field(None, description="Style for two speakers")

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "The impact of artificial intelligence on modern healthcare",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "duration": 7,
                "speaker_mode": "two",
                "conversation_style": "professional"
            }
        }


class CategoryResponse(BaseModel):
    """Response schema for category"""
    id: UUID
    name: str
    description: Optional[str]
    icon: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PodcastResponse(BaseModel):
    """Response schema for podcast"""
    id: UUID
    user_id: int
    category_id: UUID
    topic: str
    duration: int
    speaker_mode: SpeakerMode
    voice_type: Optional[VoiceType] = None
    conversation_style: Optional[ConversationStyle] = None
    status: PodcastStatus
    is_public: bool
    audio_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    script: Optional[str] = None
    error_message: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True


class PodcastListResponse(BaseModel):
    """Response schema for listing podcasts"""
    podcasts: list[PodcastResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PodcastStatusResponse(BaseModel):
    """Response schema for podcast status"""
    id: UUID
    status: PodcastStatus
    progress: Optional[int] = Field(None, description="Progress percentage (0-100)")
    stage: Optional[str] = Field(None, description="Current generation stage")
    audio_url: Optional[str]
    error_message: Optional[str]


class PodcastPublishRequest(BaseModel):
    """Request schema for publishing/unpublishing a podcast"""
    is_public: bool = Field(..., description="Make podcast public or private")
