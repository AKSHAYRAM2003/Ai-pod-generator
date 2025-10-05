"""
Audio Utilities
Helper functions for audio processing and conversion
"""
import io
import wave
from typing import Optional
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)

# Audio settings
SAMPLE_RATE = 24000  # 24kHz for high quality
CHANNELS = 1  # Mono
SAMPLE_WIDTH = 2  # 16-bit


def pcm_to_wav(pcm_data: bytes, sample_rate: int = SAMPLE_RATE) -> bytes:
    """
    Convert raw PCM audio data to WAV format
    
    Args:
        pcm_data: Raw PCM audio bytes
        sample_rate: Sample rate (default 24000)
        
    Returns:
        WAV format audio bytes
    """
    try:
        # Create in-memory WAV file
        wav_io = io.BytesIO()
        
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(SAMPLE_WIDTH)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
        
        wav_io.seek(0)
        return wav_io.read()
        
    except Exception as e:
        logger.error(f"Error converting PCM to WAV: {e}")
        raise


def wav_to_mp3(wav_data: bytes, bitrate: str = "192k") -> bytes:
    """
    Convert WAV audio to MP3 format
    
    Args:
        wav_data: WAV format audio bytes
        bitrate: MP3 bitrate (default 192k for high quality)
        
    Returns:
        MP3 format audio bytes
    """
    try:
        # Load WAV from bytes
        wav_io = io.BytesIO(wav_data)
        audio = AudioSegment.from_wav(wav_io)
        
        # Export as MP3
        mp3_io = io.BytesIO()
        audio.export(
            mp3_io,
            format="mp3",
            bitrate=bitrate,
            parameters=["-q:a", "0"]  # Highest quality
        )
        
        mp3_io.seek(0)
        return mp3_io.read()
        
    except Exception as e:
        logger.error(f"Error converting WAV to MP3: {e}")
        raise


def pcm_to_mp3(pcm_data: bytes, sample_rate: int = SAMPLE_RATE, bitrate: str = "192k") -> bytes:
    """
    Convert raw PCM audio directly to MP3 format
    
    Args:
        pcm_data: Raw PCM audio bytes
        sample_rate: Sample rate (default 24000)
        bitrate: MP3 bitrate (default 192k)
        
    Returns:
        MP3 format audio bytes
    """
    try:
        # First convert to WAV
        wav_data = pcm_to_wav(pcm_data, sample_rate)
        
        # Then convert to MP3
        mp3_data = wav_to_mp3(wav_data, bitrate)
        
        return mp3_data
        
    except Exception as e:
        logger.error(f"Error converting PCM to MP3: {e}")
        raise


def get_audio_duration(audio_data: bytes, format: str = "mp3") -> Optional[float]:
    """
    Get duration of audio in seconds
    
    Args:
        audio_data: Audio bytes
        format: Audio format (mp3, wav, etc.)
        
    Returns:
        Duration in seconds, or None if error
    """
    try:
        audio_io = io.BytesIO(audio_data)
        audio = AudioSegment.from_file(audio_io, format=format)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
        
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return None


def validate_audio(audio_data: bytes) -> bool:
    """
    Validate that audio data is valid
    
    Args:
        audio_data: Audio bytes to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if not audio_data or len(audio_data) == 0:
            return False
        
        # Try to load as audio
        audio_io = io.BytesIO(audio_data)
        AudioSegment.from_mp3(audio_io)
        return True
        
    except Exception:
        return False
