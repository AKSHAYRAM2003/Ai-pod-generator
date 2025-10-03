"""
Script to delete a specific user by email
"""
import asyncio
from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal
from app.models.user import User

async def delete_user_by_email(email: str):
    async with AsyncSessionLocal() as session:
        # Find the user first to show info
        result = await session.execute(
            select(User).where(User.email == email.lower())
        )
        user = result.scalar_one_or_none()
        
        if user:
            print(f"Found user: {user.email} (ID: {user.id})")
            print(f"  Name: {user.first_name} {user.last_name}")
            print(f"  Has avatar: {'Yes' if user.avatar_url else 'No'}")
            print(f"  Created: {user.created_at}")
            
            # Delete the user
            delete_result = await session.execute(
                delete(User).where(User.email == email.lower())
            )
            await session.commit()
            print(f"\n✅ Successfully deleted user: {email}")
        else:
            print(f"❌ User not found: {email}")

if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else "ramakshay100@gmail.com"
    asyncio.run(delete_user_by_email(email))
