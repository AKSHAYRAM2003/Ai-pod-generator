"""
Thumbnail Generation Service
Generates AI thumbnails for podcasts using Gemini Imagen
"""
import logging
import base64
import io
import os
from typing import Optional
from PIL import Image
from google import genai
from google.genai import types
from google.auth import default
from google.oauth2 import service_account

from app.core.gemini_config import (
    GEMINI_API_KEY, 
    GCP_PROJECT_ID, 
    GCP_LOCATION,
    GCP_CREDENTIALS_PATH
)

logger = logging.getLogger(__name__)

# Use Imagen 4.0 for best quality image generation
IMAGE_MODEL = "imagen-4.0-generate-001"


class ThumbnailService:
    """Service for generating podcast thumbnails using Gemini Imagen"""
    
    def __init__(self):
        # Initialize client with service account credentials for Vertex AI
        try:
            if GCP_CREDENTIALS_PATH and os.path.exists(GCP_CREDENTIALS_PATH):
                logger.info(f"Using service account credentials from: {GCP_CREDENTIALS_PATH}")
                credentials = service_account.Credentials.from_service_account_file(
                    GCP_CREDENTIALS_PATH,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                self.client = genai.Client(
                    vertexai=True,
                    project=GCP_PROJECT_ID,
                    location=GCP_LOCATION,
                    credentials=credentials
                )
                logger.info(f"Initialized Vertex AI client with project: {GCP_PROJECT_ID}, location: {GCP_LOCATION}")
            else:
                logger.warning(f"Service account file not found at: {GCP_CREDENTIALS_PATH}")
                logger.info("Falling back to API key authentication")
                self.client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception as e:
            logger.warning(f"Failed to initialize Vertex AI client: {e}")
            logger.warning("Falling back to API key authentication (limited Imagen support)")
            self.client = genai.Client(api_key=GEMINI_API_KEY)
    
    def generate_thumbnail_sync(
        self,
        topic: str,
        description: str,
        category_name: Optional[str] = None,
    ) -> bytes:
        """
        Synchronous version of thumbnail generation (for Celery tasks)
        
        Args:
            topic: Podcast topic
            description: Podcast description
            category_name: Category name for context
            
        Returns:
            Image bytes in PNG format
        """
        logger.info(f"Generating thumbnail (sync) for topic: {topic}")
        
        try:
            # Build image generation prompt
            prompt = self._build_image_prompt(topic, description, category_name)
            
            logger.info(f"Image prompt: {prompt}")
            
            # Use Imagen API to generate image (synchronous call)
            response = self.client.models.generate_images(
                model=IMAGE_MODEL,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="1:1",
                    safety_filter_level="block_some",
                    person_generation="allow_adult",
                )
            )
            
            # Extract image from response
            if response.generated_images and len(response.generated_images) > 0:
                generated_image = response.generated_images[0]
                
                # Get image bytes from the Gemini Image object
                if hasattr(generated_image, 'image') and generated_image.image:
                    image_obj = generated_image.image
                    
                    # Gemini Image has image_bytes attribute
                    if hasattr(image_obj, 'image_bytes') and image_obj.image_bytes:
                        image_data = image_obj.image_bytes
                        logger.info(f"Generated thumbnail, original size: {len(image_data)} bytes")
                        
                        # Optimize image size while maintaining quality
                        optimized_data = self._optimize_image(image_data)
                        logger.info(f"Optimized thumbnail, final size: {len(optimized_data)} bytes")
                        
                        return optimized_data
                    else:
                        logger.error(f"Image object attributes: {dir(image_obj)}")
                        raise Exception("Image object does not have image_bytes")
                else:
                    logger.error(f"Generated image attributes: {dir(generated_image)}")
                    raise Exception("Image object does not have expected format")
            
            raise Exception("No image data found in Gemini response")
                
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            logger.error(f"Full error details: {str(e)}")
            # Create a simple placeholder image as fallback
            return self._create_placeholder_image(topic)
    
    async def generate_thumbnail(
        self,
        topic: str,
        description: str,
        category_name: Optional[str] = None,
    ) -> bytes:
        """
        Generate a podcast thumbnail image using Gemini Imagen
        
        Args:
            topic: Podcast topic
            description: Podcast description
            category_name: Category name for context
            
        Returns:
            Image bytes in PNG format
        """
        # Just call the sync version for now
        return self.generate_thumbnail_sync(topic, description, category_name)
    
    def _build_image_prompt(
        self,
        topic: str,
        description: str,
        category_name: Optional[str] = None,
    ) -> str:
        """
        Build intelligent, content-aware image generation prompt
        Creates unique Studio Ghibli-style scenes based on podcast topic
        """
        
        # Analyze topic to create specific scene
        topic_lower = topic.lower()
        
        # Scene mapping based on topic keywords
        scene = self._generate_scene_from_topic(topic_lower, category_name)
        
        # Build complete prompt following best practices
        prompt = f"""Create a podcast thumbnail about {topic}. {scene}, in the style of Studio Ghibli animation, soft lighting, warm inviting colors, detailed painterly textures, anime-style characters, include human characters, cinematic composition, center focus on main character, clear space at top for title text, bright and optimistic tone, visually balanced and not cluttered, perfect for podcast cover art."""
        
        # Clean up extra whitespace
        prompt = " ".join(prompt.split())
        
        return prompt
    
    def _generate_scene_from_topic(self, topic: str, category: Optional[str]) -> str:
        """Generate specific, realistic scene description with human characters based on topic keywords"""
        
        # AI/Technology topics - with specific business contexts
        if any(word in topic for word in ['small business', 'businesses using ai']):
            return "Scene: A smiling small shop owner sitting at a wooden desk using a laptop, surrounded by soft glowing AI holographic icons floating around, cozy shop interior with shelves of products, potted plants on windowsill, warm morning sunlight streaming through large windows, friendly and hopeful atmosphere, anime-style character with expressive face"
        
        elif any(word in topic for word in ['ai', 'artificial intelligence', 'future of ai']):
            if 'job' in topic or 'work' in topic or 'everyday' in topic:
                return "Scene: Diverse office workers (2-3 people) collaborating with friendly translucent AI assistants, modern bright workspace with floor-to-ceiling windows showing city skyline, green plants on desks, laptops with holographic displays, hopeful and productive atmosphere, anime-style characters engaged in work"
            elif 'music' in topic or 'artist' in topic:
                return "Scene: A musician in a creative studio surrounded by floating musical notes and AI-assisted instruments, vinyl records on wooden shelves, warm vintage Edison bulb lighting, person playing piano or guitar with magical digital elements around them, inspiring and artistic atmosphere, anime-style character with passionate expression"
            else:
                return "Scene: A friendly researcher in a cozy modern lab using a laptop at a glass desk, surrounded by gentle glowing AI holograms and floating neural network visualizations in blue and purple, large windows with natural light, indoor plants, warm and inviting tech atmosphere, anime-style character with curious expression"
        
        # Energy/Environment topics
        elif any(word in topic for word in ['renewable energy', 'solar', 'wind energy', 'clean energy', 'future of renewable']):
            return "Scene: An engineer (young professional with safety vest) overlooking a beautiful landscape with modern wind turbines and solar panels integrated into rolling green hills, bright sunny day with blue sky and white clouds, birds flying, hopeful sustainable future vision, anime-style character looking confident and optimistic"
        
        elif any(word in topic for word in ['environment', 'sustainability', 'climate', 'nature']):
            return "Scene: A person planting a young tree in a lush green forest, sunlight filtering through leaves creating dappled light, gentle morning mist, butterflies and small animals nearby, hands in soil connecting with nature, hopeful environmental restoration theme, anime-style character with caring expression"
        
        # Business topics
        elif any(word in topic for word in ['business', 'entrepreneur', 'startup', 'company']):
            return "Scene: Young entrepreneurs (2-3 people) brainstorming with sticky notes and whiteboards in a bright creative office space, large windows with city view, laptops and coffee cups on wooden table, collaborative energy and excitement, modern casual office with plants, inspiring startup culture, anime-style characters with enthusiastic expressions"
        
        # Health/Wellness topics
        elif any(word in topic for word in ['health', 'wellness', 'medical', 'healthcare', 'doctor']):
            return "Scene: A caring doctor or nurse in a peaceful medical office with large windows bringing natural light, medical charts on digital screens, potted plants creating calm atmosphere, person in white coat smiling warmly at viewer, warm and reassuring healthcare setting, anime-style character with kind expression"
        
        elif any(word in topic for word in ['fitness', 'exercise', 'sports', 'training']):
            return "Scene: An athlete training in a beautiful outdoor setting during golden hour, person stretching or jogging on a path through a park, morning light creating long shadows, determined but joyful expression, natural landscape with trees in background, inspiring fitness journey, anime-style character in athletic wear"
        
        # Education/Learning topics
        elif any(word in topic for word in ['education', 'learning', 'school', 'teaching', 'knowledge']):
            return "Scene: A warm classroom with a friendly teacher and engaged students, books and papers floating magically around them like in a dream, large windows with natural sunlight, wooden desks, chalkboard with colorful diagrams, inspiring learning atmosphere, anime-style characters with excited expressions about discovery"
        
        # Arts/Culture topics
        elif any(word in topic for word in ['art', 'painting', 'creativity', 'design', 'creative']):
            return "Scene: An artist in a sunlit studio working on a colorful canvas on an easel, paint brushes in hand, palette with vibrant colors, paintings on walls, large windows with afternoon light, creative clutter of art supplies, inspiring artistic atmosphere, anime-style character with focused creative expression"
        
        elif any(word in topic for word in ['music', 'musician', 'sound', 'audio']):
            return "Scene: A musician in a cozy home studio with acoustic guitar in hands, surrounded by vintage microphones and musical equipment, vinyl records and cassettes on shelves, warm ambient lighting from string lights, person creating music with passion, intimate recording space, anime-style character with peaceful expression"
        
        # Food topics
        elif any(word in topic for word in ['food', 'cooking', 'restaurant', 'cuisine', 'chef']):
            return "Scene: A cheerful chef in a warm kitchen preparing fresh ingredients on a wooden cutting board, steam rising from pots on stove, herbs hanging to dry, fresh vegetables displayed, copper pots on walls, natural light from window, inviting and delicious atmosphere, anime-style character with happy expression"
        
        # Travel/Adventure topics
        elif any(word in topic for word in ['travel', 'adventure', 'journey', 'explore', 'world']):
            return "Scene: A traveler with a backpack standing at a scenic mountain viewpoint overlooking valleys and distant peaks, golden hour lighting creating warm glow, map in hand, camera around neck, sense of wonder and freedom, beautiful landscape spreading below, anime-style character with adventurous smile"
        
        # Minimalism/Lifestyle topics
        elif any(word in topic for word in ['minimalism', 'lifestyle', 'simple', 'consumer culture']):
            return "Scene: A peaceful person sitting cross-legged in a beautifully simple apartment with minimal furniture (low table, floor cushions), large windows with natural light and city view, single potted plant, wooden floors, sense of calm and intentional living, zen-like atmosphere, anime-style character with serene expression"
        
        # Science topics
        elif any(word in topic for word in ['science', 'research', 'discovery', 'laboratory']):
            return "Scene: A scientist in a bright laboratory examining samples under a microscope, beakers with colorful liquids bubbling gently, plants in the background for bio research, large windows with natural light, notebooks and equipment organized neatly, sense of discovery and wonder, anime-style character with curious expression"
        
        elif any(word in topic for word in ['space', 'astronomy', 'cosmos', 'universe']):
            return "Scene: An astronomer in an observatory at night looking through a large telescope, starry sky visible through dome opening, constellation charts on walls, warm lamp light on desk, magical and wondrous atmosphere, anime-style character with awe-struck expression"
        
        # Finance topics
        elif any(word in topic for word in ['finance', 'economics', 'money', 'investment', 'market']):
            return "Scene: A professional analyst in a modern office reviewing holographic financial charts and graphs floating in air, floor-to-ceiling windows showing city skyline at dusk, sleek desk with multiple screens, confident and prosperous atmosphere, anime-style character with professional appearance and confident expression"
        
        # Gaming topics
        elif any(word in topic for word in ['gaming', 'video games', 'esports', 'gamer']):
            return "Scene: A gamer in a cozy gaming room with warm RGB ambient lighting, comfortable gaming chair, dual monitors showing colorful fantasy game worlds, headphones on desk, gaming posters on walls, immersive but balanced atmosphere, anime-style character with focused but happy expression"
        
        # History topics
        elif any(word in topic for word in ['history', 'historical', 'past', 'ancient']):
            return "Scene: A historian in a beautiful old library examining ancient books and scrolls on a wooden desk, towering bookshelves filled with leather-bound tomes, warm lamp light creating cozy atmosphere, magnifying glass and old documents, sense of discovery and reverence for past, anime-style character with scholarly appearance"
        
        # Default general scene with character
        else:
            return f"Scene: A thoughtful person working on a laptop in a bright inspiring workspace, large windows with natural light and green view, indoor plants nearby, notebooks and coffee cup on wooden desk, warm and hopeful atmosphere related to {topic}, anime-style character with engaged expression"
    
    def _create_placeholder_image(self, topic: str) -> bytes:
        """Create a topic-specific artistic placeholder image when generation fails"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import hashlib
            
            # Generate unique colors based on topic
            topic_hash = int(hashlib.md5(topic.encode()).hexdigest(), 16)
            
            # Create varied color schemes based on topic hash
            color_schemes = [
                # Tech/AI - Blue/Purple
                [(30, 30, 80), (80, 50, 150), (120, 80, 200)],
                # Nature/Energy - Green/Yellow
                [(20, 60, 30), (60, 120, 40), (100, 180, 60)],
                # Business - Orange/Red
                [(80, 40, 20), (150, 80, 40), (200, 120, 60)],
                # Health - Teal/Cyan
                [(20, 80, 80), (40, 140, 140), (60, 180, 180)],
                # Arts - Pink/Purple
                [(80, 30, 60), (140, 60, 100), (180, 90, 140)],
                # Education - Yellow/Orange
                [(80, 60, 20), (160, 120, 40), (200, 160, 80)],
            ]
            
            scheme = color_schemes[topic_hash % len(color_schemes)]
            
            # Create gradient background
            img = Image.new('RGB', (512, 512))
            draw = ImageDraw.Draw(img)
            
            # Multi-color gradient
            for i in range(512):
                progress = i / 512
                if progress < 0.5:
                    # First half: scheme[0] to scheme[1]
                    t = progress * 2
                    color = tuple(int(scheme[0][j] + (scheme[1][j] - scheme[0][j]) * t) for j in range(3))
                else:
                    # Second half: scheme[1] to scheme[2]
                    t = (progress - 0.5) * 2
                    color = tuple(int(scheme[1][j] + (scheme[2][j] - scheme[1][j]) * t) for j in range(3))
                draw.rectangle([(0, i), (512, i+1)], fill=color)
            
            # Add subtle circular overlay for depth
            overlay = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Draw semi-transparent circles for artistic effect
            for radius in [350, 250, 150]:
                alpha = 30
                overlay_draw.ellipse(
                    [(256 - radius, 256 - radius), (256 + radius, 256 + radius)],
                    fill=(255, 255, 255, alpha)
                )
            
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            
            # Add podcast emoji in center
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 120)
            except:
                font = None
            
            text = "🎙️"
            if font:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                position = ((512 - text_width) // 2, (512 - text_height) // 2)
                draw.text(position, text, font=font, fill=(255, 255, 255, 200))
            
            # Save to bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG', quality=95)
            return img_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating placeholder: {e}")
            # Return minimal gradient image as last resort
            img = Image.new('RGB', (512, 512))
            draw = ImageDraw.Draw(img)
            for i in range(512):
                color = (30 + i // 8, 30 + i // 10, 50 + i // 6)
                draw.rectangle([(0, i), (512, i+1)], fill=color)
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            return img_buffer.getvalue()
    
    def _optimize_image(self, image_data: bytes) -> bytes:
        """
        Optimize image size while maintaining quality
        - Resize to optimal dimensions (512x512 for thumbnails)
        - Compress with high quality JPEG
        - Target size: 50-150KB (much smaller than original ~1.5MB)
        """
        try:
            # Load image from bytes
            img = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary (for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize to optimal thumbnail size (512x512)
            # This is perfect for podcast thumbnails - visible but not huge
            target_size = (512, 512)
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Save as optimized JPEG with high quality
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            optimized_data = output.getvalue()
            
            # Calculate compression ratio
            original_size = len(image_data)
            optimized_size = len(optimized_data)
            ratio = (1 - optimized_size / original_size) * 100
            
            logger.info(f"Image optimized: {original_size:,} bytes → {optimized_size:,} bytes ({ratio:.1f}% reduction)")
            
            return optimized_data
            
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            # Return original if optimization fails
            return image_data


# Singleton instance
thumbnail_service = ThumbnailService()
