"""
Gemini API Configuration
Configuration for Google Gemini AI for podcast generation
"""
import os
from google import genai
from google.genai import types

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDzhIpsf8RZTUnIpH4Z00dG2ltUiULYC2A")

# GCP Configuration for Vertex AI (Imagen)
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "sylvan-box-474408-r3")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")

# Models
TEXT_MODEL = "models/gemini-2.0-flash-exp"  # For script generation
AUDIO_MODEL = "models/gemini-2.0-flash-exp"  # For audio synthesis with native audio

# Voice Configuration
# Best voices for natural sounding audio
MALE_VOICE = "Puck"  # Male voice - natural and professional
FEMALE_VOICE = "Kore"  # Female voice - warm and engaging

# Alternative voices (for future use)
VOICE_OPTIONS = {
    "male": ["Puck", "Charon", "Kore"],
    "female": ["Kore", "Aoede", "Fenrir"]
}

# Audio Configuration
AUDIO_CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    media_resolution="MEDIA_RESOLUTION_MEDIUM",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Puck"  # Default voice, will be changed dynamically
            )
        )
    ),
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=25600,
        sliding_window=types.SlidingWindow(target_tokens=12800),
    ),
)

# Audio format settings
SEND_SAMPLE_RATE = 16000  # Input sample rate
RECEIVE_SAMPLE_RATE = 24000  # Output sample rate (high quality)
AUDIO_FORMAT = "mp3"  # Output format
AUDIO_BITRATE = "192k"  # High quality bitrate for natural sound

# Generation timeouts
SCRIPT_GENERATION_TIMEOUT = 180  # 3 minutes for script generation
AUDIO_GENERATION_TIMEOUT = 600  # 10 minutes for audio generation (increased for reliability)

# Retry configuration
MAX_RETRIES = 2  # Number of retries for failed operations
RETRY_DELAY = 5  # Delay between retries in seconds

# Initialize Gemini Client
def get_gemini_client():
    """Get initialized Gemini client"""
    return genai.Client(
        http_options={"api_version": "v1alpha"},
        api_key=GEMINI_API_KEY,
    )
