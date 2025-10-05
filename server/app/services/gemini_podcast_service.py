"""
Gemini Podcast Generation Service
Handles AI-powered podcast script and audio generation using Google Gemini
"""
import asyncio
import io
import base64
from typing import Optional, Dict, Any
import logging

from google import genai
from google.genai import types

from app.core.gemini_config import (
    get_gemini_client,
    TEXT_MODEL,
    AUDIO_MODEL,
    MALE_VOICE,
    FEMALE_VOICE,
    RECEIVE_SAMPLE_RATE,
    SCRIPT_GENERATION_TIMEOUT,
    AUDIO_GENERATION_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
)
from app.models.podcast import SpeakerMode, VoiceType, ConversationStyle

logger = logging.getLogger(__name__)


class GeminiPodcastService:
    """Service for generating podcasts using Gemini AI"""
    
    def __init__(self):
        self.client = get_gemini_client()
    
    async def generate_podcast_script(
        self,
        topic: str,
        description: str,
        duration: int,  # in minutes
        speaker_mode: SpeakerMode,
        voice_type: Optional[VoiceType] = None,
        conversation_style: Optional[ConversationStyle] = None,
    ) -> str:
        """
        Generate podcast script using Gemini
        
        Args:
            topic: Podcast topic
            description: Detailed description
            duration: Duration in minutes (5, 7, or 10)
            speaker_mode: Single or two speakers
            voice_type: Male/Female for single speaker
            conversation_style: Style for two-speaker podcasts
            
        Returns:
            Generated script as string
        """
        logger.info(f"Generating script for topic: {topic}, duration: {duration}min, mode: {speaker_mode}")
        
        # Retry logic for script generation
        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt}/{MAX_RETRIES} for script generation")
                    await asyncio.sleep(RETRY_DELAY)
                
                # Build prompt based on speaker mode
                if speaker_mode == SpeakerMode.SINGLE:
                    prompt = self._build_single_speaker_prompt(topic, description, duration, voice_type)
                else:
                    prompt = self._build_two_speaker_prompt(topic, description, duration, conversation_style)
                
                # Generate script using Gemini
                response = await asyncio.wait_for(
                    self._generate_text(prompt),
                    timeout=SCRIPT_GENERATION_TIMEOUT
                )
                
                logger.info(f"Script generated successfully, length: {len(response)} characters")
                return response
                
            except asyncio.TimeoutError:
                last_error = Exception(f"Script generation timed out after {SCRIPT_GENERATION_TIMEOUT} seconds")
                logger.error(f"Attempt {attempt + 1}: {last_error}")
                if attempt >= MAX_RETRIES:
                    raise last_error
            except Exception as e:
                last_error = e
                logger.error(f"Attempt {attempt + 1}: Error generating script: {e}")
                if attempt >= MAX_RETRIES:
                    raise Exception(f"Failed to generate script after {MAX_RETRIES + 1} attempts: {str(e)}")
        
        # This should never be reached, but just in case
        raise last_error or Exception("Script generation failed")
    
    async def generate_podcast_audio(
        self,
        script: str,
        speaker_mode: SpeakerMode,
        voice_type: Optional[VoiceType] = None,
    ) -> bytes:
        """
        Generate audio from script using Gemini native audio
        
        Args:
            script: The podcast script
            speaker_mode: Single or two speakers
            voice_type: Male/Female for single speaker
            
        Returns:
            Audio data as bytes (PCM format)
        """
        logger.info(f"Generating audio, mode: {speaker_mode}, voice: {voice_type}")
        
        # Retry logic for audio generation
        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt}/{MAX_RETRIES} for audio generation")
                    await asyncio.sleep(RETRY_DELAY)
                
                if speaker_mode == SpeakerMode.SINGLE:
                    # Single speaker audio generation
                    voice_name = MALE_VOICE if voice_type == VoiceType.MALE else FEMALE_VOICE
                    audio_data = await asyncio.wait_for(
                        self._generate_single_speaker_audio(script, voice_name),
                        timeout=AUDIO_GENERATION_TIMEOUT
                    )
                else:
                    # Two speaker audio generation (conversation)
                    audio_data = await asyncio.wait_for(
                        self._generate_two_speaker_audio(script),
                        timeout=AUDIO_GENERATION_TIMEOUT
                    )
                
                logger.info(f"Audio generated successfully, size: {len(audio_data)} bytes")
                return audio_data
                
            except asyncio.TimeoutError:
                last_error = Exception(f"Audio generation timed out after {AUDIO_GENERATION_TIMEOUT} seconds")
                logger.error(f"Attempt {attempt + 1}: {last_error}")
                if attempt >= MAX_RETRIES:
                    raise last_error
            except Exception as e:
                last_error = e
                logger.error(f"Attempt {attempt + 1}: Error generating audio: {e}")
                if attempt >= MAX_RETRIES:
                    raise Exception(f"Failed to generate audio after {MAX_RETRIES + 1} attempts: {str(e)}")
        
        # This should never be reached, but just in case
        raise last_error or Exception("Audio generation failed")
    
    async def _generate_text(self, prompt: str) -> str:
        """Generate text using Gemini"""
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=TEXT_MODEL,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini text generation error: {e}")
            raise
    
    async def _generate_single_speaker_audio(self, script: str, voice_name: str) -> bytes:
        """Generate audio for single speaker using Gemini Live API"""
        try:
            logger.info(f"Generating single speaker audio with voice: {voice_name}")
            
            # Configure for single speaker
            config = types.LiveConnectConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name
                        )
                    )
                ),
            )
            
            audio_chunks = []
            
            async with self.client.aio.live.connect(model=AUDIO_MODEL, config=config) as session:
                # Send script to be converted to audio
                logger.info(f"Sending script to audio generation (length: {len(script)} chars)")
                await session.send(input=script, end_of_turn=True)
                
                # Collect audio chunks
                chunk_count = 0
                async for response in session.receive():
                    if response.data:
                        audio_chunks.append(response.data)
                        chunk_count += 1
                
                logger.info(f"Received {chunk_count} audio chunks")
            
            if not audio_chunks:
                raise Exception("No audio data received from Gemini API")
            
            # Combine all audio chunks
            combined_audio = b''.join(audio_chunks)
            logger.info(f"Combined audio size: {len(combined_audio)} bytes")
            return combined_audio
            
        except Exception as e:
            logger.error(f"Single speaker audio generation error: {e}")
            raise
    
    async def _generate_two_speaker_audio(self, script: str) -> bytes:
        """Generate audio for two speakers (male + female)"""
        try:
            # Parse script to identify speaker parts
            parts = self._parse_two_speaker_script(script)
            
            if not parts:
                raise Exception("Failed to parse script - no speaker parts found")
            
            logger.info(f"Parsed script into {len(parts)} parts")
            
            audio_chunks = []
            
            for idx, (speaker_num, text) in enumerate(parts):
                if not text.strip():
                    continue
                
                # Alternate between male and female voices
                voice_name = MALE_VOICE if speaker_num == 1 else FEMALE_VOICE
                
                logger.info(f"Generating audio for part {idx + 1}/{len(parts)} - Speaker {speaker_num} ({voice_name}): {text[:50]}...")
                
                config = types.LiveConnectConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name
                            )
                        )
                    ),
                )
                
                try:
                    async with self.client.aio.live.connect(model=AUDIO_MODEL, config=config) as session:
                        await session.send(input=text, end_of_turn=True)
                        
                        part_chunks = []
                        async for response in session.receive():
                            if response.data:
                                part_chunks.append(response.data)
                        
                        if part_chunks:
                            audio_chunks.extend(part_chunks)
                            logger.info(f"Part {idx + 1} generated successfully, {len(part_chunks)} chunks")
                        else:
                            logger.warning(f"Part {idx + 1} generated no audio chunks")
                            
                except Exception as part_error:
                    logger.error(f"Error generating audio for part {idx + 1}: {part_error}")
                    # Continue with next part instead of failing completely
                    continue
            
            if not audio_chunks:
                raise Exception("No audio chunks were generated from the script")
            
            # Combine all audio chunks
            combined_audio = b''.join(audio_chunks)
            logger.info(f"Combined all audio chunks, total size: {len(combined_audio)} bytes")
            return combined_audio
            
        except Exception as e:
            logger.error(f"Two speaker audio generation error: {e}")
            raise
    
    def _parse_two_speaker_script(self, script: str) -> list:
        """Parse two-speaker script into parts"""
        parts = []
        lines = script.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for speaker labels (support multiple formats)
            # Alex (Speaker 1) = Male voice (speaker 1)
            # Sarah (Speaker 2) = Female voice (speaker 2)
            if any(prefix in line for prefix in ['Alex:', 'Speaker 1:', 'Host:', 'Male:']):
                # Extract text after the colon
                if ':' in line:
                    text = line.split(':', 1)[1].strip()
                    parts.append((1, text))
            elif any(prefix in line for prefix in ['Sarah:', 'Speaker 2:', 'Guest:', 'Female:']):
                # Extract text after the colon
                if ':' in line:
                    text = line.split(':', 1)[1].strip()
                    parts.append((2, text))
            elif ':' in line:
                # Try to detect speaker by position (odd = speaker 1, even = speaker 2)
                text = line.split(':', 1)[1].strip()
                speaker_num = 1 if len(parts) % 2 == 0 else 2
                parts.append((speaker_num, text))
            else:
                # If no clear speaker, add to last speaker or default to speaker 1
                if parts and len(line) > 0:
                    last_speaker = parts[-1][0]
                    parts[-1] = (last_speaker, parts[-1][1] + " " + line)
                elif line:
                    parts.append((1, line))
        
        return parts
    
    def _build_single_speaker_prompt(
        self,
        topic: str,
        description: str,
        duration: int,
        voice_type: Optional[VoiceType]
    ) -> str:
        """Build prompt for single speaker podcast"""
        # Determine speaker name - opposite gender for addressing
        if voice_type == VoiceType.MALE:
            speaker_name = "Alex"  # Male voice
            voice_desc = "male"
        else:
            speaker_name = "Sarah"  # Female voice
            voice_desc = "female"
        
        # Calculate target word count (150 words per minute)
        word_count = duration * 150
        
        return f"""Create a {duration}-minute podcast script about {topic}.

Description: {description}

Requirements:
- Single speaker ({voice_desc} voice - Speaker name: {speaker_name})
- Duration: EXACTLY {duration} minutes when spoken at normal pace
- Word Count: approximately {word_count} words (150 words per minute)
- Format: Professional, engaging, conversational monologue
- Include: Proper introduction with host name, main content (3-5 key points), and conclusion with outro
- Tone: Informative, friendly, and natural
- Style: As if speaking directly to the listener

CRITICAL REQUIREMENTS:
1. START with a proper introduction: "{speaker_name} here, and welcome to today's podcast where we'll be exploring {topic}."
2. END with a proper outro: "This has been {speaker_name}, thank you for listening, and I'll catch you in the next episode!"
3. Use the speaker's name naturally throughout (e.g., "I'm {speaker_name}, and I believe...")
4. IMPORTANT: The script MUST be approximately {word_count} words long to fill {duration} minutes of speaking time

Structure:
1. Opening Hook (5-10 seconds): Grab attention with an interesting question or fact
2. Introduction (15-20 seconds): Introduce yourself ({speaker_name}) and the topic clearly
3. Main Content (70-80% of duration): 
   - Dive deep into 3-5 key points
   - Use examples, stories, and analogies
   - Maintain conversational flow
   - This is the longest section - make it comprehensive and detailed
4. Conclusion (15-20 seconds): Summarize key takeaways
5. Outro (5-10 seconds): Thank listeners and sign off with your name

Write the complete script in a natural speaking style, as it would be spoken aloud.
Do not include any stage directions, labels, or formatting - just the spoken words as {speaker_name} would say them.
Make it sound like a real person talking, not reading from a script.
Remember: Target {word_count} words for a {duration}-minute podcast!"""
    
    def _build_two_speaker_prompt(
        self,
        topic: str,
        description: str,
        duration: int,
        conversation_style: Optional[ConversationStyle]
    ) -> str:
        """Build prompt for two-speaker podcast"""
        
        # Speaker 1: Male voice (uses name Alex)
        # Speaker 2: Female voice (uses name Sarah)
        speaker_1_name = "Alex"
        speaker_2_name = "Sarah"
        
        # Calculate target word count (150 words per minute)
        word_count = duration * 150
        
        style_descriptions = {
            ConversationStyle.CASUAL: "casual, friendly conversation between two colleagues",
            ConversationStyle.PROFESSIONAL: "professional discussion with industry experts sharing insights",
            ConversationStyle.EDUCATIONAL: "educational discussion where Alex (expert) explains concepts to Sarah (learner), with Sarah asking clarifying questions",
        }
        
        style_desc = style_descriptions.get(conversation_style, "engaging dialogue")
        
        return f"""Create a {duration}-minute two-speaker podcast script about {topic}.

Description: {description}

Requirements:
- Speaker 1: {speaker_1_name} (male voice) - First speaker
- Speaker 2: {speaker_2_name} (female voice) - Second speaker
- Duration: EXACTLY {duration} minutes when spoken at normal pace
- Word Count: approximately {word_count} words total (150 words per minute)
- Format: {style_desc}
- Include: Proper introduction with both names, main discussion (3-5 key points), and conclusion with proper outro
- Tone: Natural, engaging, and authentic
- Style: Back-and-forth dialogue that flows naturally

CRITICAL REQUIREMENTS:
1. START with introductions:
   {speaker_1_name}: "Hey everyone, I'm {speaker_1_name}"
   {speaker_2_name}: "And I'm {speaker_2_name}, and today we're diving into {topic}"

2. Throughout the conversation:
   - Address each other by name occasionally (e.g., "{speaker_1_name}, that's a great point" or "What do you think, {speaker_2_name}?")
   - {speaker_1_name} uses male voice, {speaker_2_name} uses female voice
   - Make it sound like a natural conversation between two people
   - IMPORTANT: The dialogue MUST total approximately {word_count} words to fill {duration} minutes

3. END with proper outro:
   {speaker_1_name}: "Well {speaker_2_name}, I think that covers everything we wanted to discuss today"
   {speaker_2_name}: "Absolutely {speaker_1_name}. Thanks everyone for listening, this has been {speaker_2_name}"
   {speaker_1_name}: "And {speaker_1_name}. Catch you in the next episode!"

Structure:
1. Opening (15-20 seconds): Both speakers introduce themselves and the topic
2. Main Discussion (70-80% of duration): 
   - Natural back-and-forth dialogue
   - 3-5 key points explored through conversation
   - Build on each other's points
   - Use each other's names naturally
3. Conclusion (10-15 seconds): Collaborative summary
4. Outro (5-10 seconds): Thank listeners and sign off with both names

Format each line exactly as:
{speaker_1_name}: [what {speaker_1_name} says]
{speaker_2_name}: [what {speaker_2_name} says]

Make the conversation feel natural with:
- Natural transitions and reactions
- Follow-up questions
- Agreement and building on points
- Occasional interjections (e.g., "Exactly!" "Right!" "That's interesting!")
- Use each other's names throughout the conversation
- Varied sentence lengths

Write the complete script as natural dialogue between {speaker_1_name} and {speaker_2_name}.
Do not include any stage directions - just the dialogue with speaker names as labels."""


# Singleton instance
gemini_service = GeminiPodcastService()
