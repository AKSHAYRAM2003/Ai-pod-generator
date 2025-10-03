"""
Script to delete all users from the database
"""
import asyncio
from sqlalchemy import delete
from app.core.database import AsyncSessionLocal
from app.models.user import User

async def clear_all_users():
    async with AsyncSessionLocal() as session:
        # Delete all users
        result = await session.execute(delete(User))
        await session.commit()
        print(f"✅ Successfully deleted {result.rowcount} users from the database")

if __name__ == "__main__":
    asyncio.run(clear_all_users())
