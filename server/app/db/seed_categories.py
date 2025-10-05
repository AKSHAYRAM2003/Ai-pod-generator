"""
Seed Categories Script
Populates the categories table with predefined podcast categories
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.category import Category


CATEGORIES = [
    {
        "name": "Technology",
        "slug": "technology",
        "description": "Tech trends, gadgets, software, AI, and innovation",
        "icon": "Cpu"
    },
    {
        "name": "Business & Finance",
        "slug": "business-finance",
        "description": "Entrepreneurship, startups, investing, and market insights",
        "icon": "TrendingUp"
    },
    {
        "name": "Education",
        "slug": "education",
        "description": "Learning, teaching, academic topics, and skill development",
        "icon": "GraduationCap"
    },
    {
        "name": "Health & Wellness",
        "slug": "health-wellness",
        "description": "Fitness, nutrition, mental health, and wellbeing",
        "icon": "Heart"
    },
    {
        "name": "Entertainment",
        "slug": "entertainment",
        "description": "Movies, TV, music, gaming, and pop culture",
        "icon": "Film"
    },
    {
        "name": "Science",
        "slug": "science",
        "description": "Scientific discoveries, research, and exploration",
        "icon": "Microscope"
    },
    {
        "name": "History",
        "slug": "history",
        "description": "Historical events, figures, and civilizations",
        "icon": "BookOpen"
    },
    {
        "name": "News & Politics",
        "slug": "news-politics",
        "description": "Current events, political analysis, and world affairs",
        "icon": "Newspaper"
    },
    {
        "name": "Sports",
        "slug": "sports",
        "description": "Athletics, competitions, teams, and sports analysis",
        "icon": "Trophy"
    },
    {
        "name": "Arts & Culture",
        "slug": "arts-culture",
        "description": "Visual arts, literature, music, and cultural topics",
        "icon": "Palette"
    }
]


async def seed_categories():
    """Seed categories into the database"""
    async with AsyncSessionLocal() as session:
        try:
            # Check if categories already exist
            result = await session.execute(select(Category))
            existing_categories = result.scalars().all()
            
            if existing_categories:
                print(f"✅ Categories already seeded ({len(existing_categories)} categories exist)")
                return
            
            # Create categories
            categories = []
            for cat_data in CATEGORIES:
                category = Category(**cat_data)
                categories.append(category)
                session.add(category)
            
            await session.commit()
            print(f"✅ Successfully seeded {len(categories)} categories!")
            
            # Display seeded categories
            for cat in categories:
                print(f"   - {cat.name} ({cat.slug})")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding categories: {e}")
            raise


if __name__ == "__main__":
    print("🌱 Seeding categories...")
    asyncio.run(seed_categories())
