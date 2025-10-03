#!/usr/bin/env python3
"""
Test login endpoint to ensure it's fast and robust
"""
import asyncio
import json
import time
from datetime import datetime

async def test_login():
    """Test the login endpoint"""
    import sys
    sys.path.append('.')
    
    from app.core.database import get_db
    from app.services.auth_service import AuthService
    from app.schemas.auth import UserLoginRequest
    
    print("🧪 Testing Login Endpoint Performance & Robustness\n")
    print("=" * 60)
    
    # Test credentials (update with a real test user)
    test_email = input("Enter test email: ").strip()
    test_password = input("Enter test password: ").strip()
    
    print("\n📊 Running login test...\n")
    
    async for db in get_db():
        try:
            auth_service = AuthService(db)
            
            # Create login request
            login_request = UserLoginRequest(
                email=test_email,
                password=test_password,
                remember_me=False
            )
            
            # Measure login time
            start_time = time.time()
            response = await auth_service.login_user(
                login_request,
                ip_address="127.0.0.1",
                user_agent="Test Script"
            )
            end_time = time.time()
            
            login_time_ms = (end_time - start_time) * 1000
            
            print("✅ LOGIN SUCCESSFUL!")
            print("=" * 60)
            print(f"⏱️  Login Time: {login_time_ms:.2f}ms")
            print(f"📧 Email: {response.user.email}")
            print(f"👤 Name: {response.user.full_name}")
            print(f"🔑 Username: {response.user.username}")
            print(f"🖼️  Avatar URL: {response.user.avatar_url or 'Not set'}")
            print(f"✉️  Email Verified: {response.user.is_email_verified}")
            print(f"📊 Status: {response.user.status}")
            print(f"🔐 Access Token Length: {len(response.access_token)} chars")
            print(f"🔄 Refresh Token Length: {len(response.refresh_token)} chars")
            print(f"⏰ Token Expires In: {response.expires_in}s")
            print(f"🕒 Last Login: {response.user.last_login_at}")
            print(f"📅 Account Created: {response.user.created_at}")
            
            # Performance check
            print("\n📈 Performance Analysis:")
            if login_time_ms < 300:
                print("   ⚡ EXCELLENT - Login is very fast!")
            elif login_time_ms < 500:
                print("   ✅ GOOD - Login is fast enough")
            elif login_time_ms < 1000:
                print("   ⚠️  OK - Login could be faster")
            else:
                print("   ❌ SLOW - Login needs optimization")
            
            # Test remember_me
            print("\n🔄 Testing Remember Me functionality...\n")
            login_request.remember_me = True
            
            start_time = time.time()
            response_rm = await auth_service.login_user(
                login_request,
                ip_address="127.0.0.1",
                user_agent="Test Script (Remember Me)"
            )
            end_time = time.time()
            
            login_time_rm_ms = (end_time - start_time) * 1000
            
            print(f"✅ Remember Me Login Time: {login_time_rm_ms:.2f}ms")
            print(f"🔐 New Access Token: {response_rm.access_token[:50]}...")
            print(f"🔄 New Refresh Token: {response_rm.refresh_token[:50]}...")
            
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ LOGIN FAILED!")
            print(f"Error: {str(e)}")
            print(f"Type: {type(e).__name__}")
            
        finally:
            break

if __name__ == "__main__":
    asyncio.run(test_login())
