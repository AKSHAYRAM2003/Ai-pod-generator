#!/usr/bin/env python3
"""
Test forgot password feature end-to-end
"""
import asyncio
import json
from datetime import datetime

async def test_forgot_password():
    """Test the forgot password flow"""
    import sys
    sys.path.append('.')
    
    from app.core.database import get_db
    from app.services.auth_service import AuthService
    from app.schemas.auth import PasswordResetRequest
    
    print("🧪 Testing Forgot Password Feature\n")
    print("=" * 60)
    
    # Get test email
    test_email = input("Enter test email: ").strip()
    
    print("\n📊 Step 1: Request Password Reset\n")
    
    async for db in get_db():
        try:
            auth_service = AuthService(db)
            
            # Step 1: Request password reset
            result = await auth_service.send_password_reset_code(
                test_email,
                ip_address="127.0.0.1",
                user_agent="Test Script"
            )
            
            print("✅ PASSWORD RESET CODE SENT!")
            print("=" * 60)
            print(f"📧 Email: {test_email}")
            print(f"📬 Message: {result['message']}")
            print("\n⚠️  CHECK YOUR EMAIL FOR THE 6-DIGIT CODE")
            print("⏰ Code expires in 10 minutes")
            print("\n" + "=" * 60)
            
            # Step 2: Prompt for code and new password
            print("\n📊 Step 2: Verify Code & Reset Password\n")
            
            reset_code = input("Enter the 6-digit code from email: ").strip()
            new_password = input("Enter new password (min 8 chars, uppercase, lowercase, number): ").strip()
            
            # Validate password
            if len(new_password) < 8:
                print("❌ Password must be at least 8 characters")
                return
            
            if not any(c.isupper() for c in new_password):
                print("❌ Password must contain at least one uppercase letter")
                return
            
            if not any(c.islower() for c in new_password):
                print("❌ Password must contain at least one lowercase letter")
                return
            
            if not any(c.isdigit() for c in new_password):
                print("❌ Password must contain at least one number")
                return
            
            # Reset password
            reset_result = await auth_service.reset_password(
                test_email,
                reset_code,
                new_password,
                ip_address="127.0.0.1",
                user_agent="Test Script"
            )
            
            print("\n✅ PASSWORD RESET SUCCESSFUL!")
            print("=" * 60)
            print(f"📬 Message: {reset_result['message']}")
            print(f"🔐 New Password: {'*' * len(new_password)}")
            print("\n✅ You can now login with your new password!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ TEST FAILED!")
            print(f"Error: {str(e)}")
            print(f"Type: {type(e).__name__}")
            
        finally:
            break

if __name__ == "__main__":
    asyncio.run(test_forgot_password())
