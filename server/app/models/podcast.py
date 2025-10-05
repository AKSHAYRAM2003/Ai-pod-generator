"""
Podcast Model
Defines user-generated AI podcasts
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class PodcastStatus(str, enum.Enum):
    """Podcast generation status"""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    PUBLISHED = "published"


class SpeakerMode(str, enum.Enum):
    """Number of speakers in podcast"""
    SINGLE = "single"
    TWO = "two"


class VoiceType(str, enum.Enum):
    """Voice type for single speaker"""
    MALE = "male"
    FEMALE = "female"


class ConversationStyle(str, enum.Enum):
    """Conversation style for two-speaker podcasts"""
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    EDUCATIONAL = "educational"


class Podcast(Base):
    __tablename__ = "podcasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Content fields
    title = Column(String(255), nullable=False)
    topic = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Generation settings
    duration = Column(Integer, nullable=False)  # Duration in minutes (5, 7, 10)
    speaker_mode = Column(SQLEnum(SpeakerMode, values_callable=lambda x: [e.value for e in x]), nullable=False, default=SpeakerMode.SINGLE)
    voice_type = Column(SQLEnum(VoiceType, values_callable=lambda x: [e.value for e in x]), nullable=True)  # For single speaker mode
    conversation_style = Column(SQLEnum(ConversationStyle, values_callable=lambda x: [e.value for e in x]), nullable=True)  # For two-speaker mode
    
    # Status and output
    status = Column(SQLEnum(PodcastStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default=PodcastStatus.DRAFT, index=True)
    is_public = Column(Boolean, default=False, nullable=False, index=True)
    
    # Generated content
    audio_url = Column(Text, nullable=True)  # URL to audio file
    audio_duration = Column(Integer, nullable=True)  # Actual duration in seconds
    thumbnail_url = Column(Text, nullable=True)  # Podcast cover image (future)
    transcript = Column(Text, nullable=True)  # Generated transcript
    script = Column(Text, nullable=True)  # Generated script before audio conversion
    
    # Metadata (using ai_metadata to avoid SQLAlchemy reserved word)
    ai_metadata = Column(JSONB, nullable=True)  # Additional AI generation metadata
    error_message = Column(Text, nullable=True)  # Error message if generation failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="podcasts")
    category = relationship("Category")

    # def __repr__(self):
    #     return f"<Podcast(id='{self.id}', title='{self.title}', status='{self.status}')>"
