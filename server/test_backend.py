#!/usr/bin/env python3
"""
Test script to verify the AI Podcast Generator backend is working correctly.
This script tests the registration and email verification flow.
"""
import asyncio
import httpx
import json
from datetime import datetime


# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@gmail.com"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "Test123!"


async def test_registration_flow():
    """Test the complete user registration flow"""
    print("🚀 Testing AI Podcast Generator Backend")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test health check
        print("1. Testing health check...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/auth/health")
            if response.status_code == 200:
                print("✅ Health check passed")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return
        
        # Test user registration
        print("\n2. Testing user registration...")
        registration_data = {
            "email": TEST_EMAIL,
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/register",
                json=registration_data
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Registration successful")
                print(f"   Message: {result.get('message')}")
                print(f"   User ID: {result.get('user_id')}")
                print(f"   📧 Check your email ({TEST_EMAIL}) for verification code!")
                
                # Prompt for verification code
                print("\n3. Email verification...")
                verification_code = input("Enter the 6-digit verification code from email: ").strip()
                
                if verification_code and len(verification_code) == 6 and verification_code.isdigit():
                    # Test email verification
                    verify_data = {
                        "email": TEST_EMAIL,
                        "code": verification_code
                    }
                    
                    verify_response = await client.post(
                        f"{BASE_URL}/api/v1/auth/verify-email",
                        json=verify_data
                    )
                    
                    if verify_response.status_code == 200:
                        verify_result = verify_response.json()
                        print(f"✅ Email verification successful!")
                        print(f"   Access Token: {verify_result.get('access_token')[:20]}...")
                        print(f"   User verified and auto-logged in!")
                        
                        # Test login
                        print("\n4. Testing login...")
                        login_data = {
                            "email": TEST_EMAIL,
                            "password": TEST_PASSWORD
                        }
                        
                        login_response = await client.post(
                            f"{BASE_URL}/api/v1/auth/login",
                            json=login_data
                        )
                        
                        if login_response.status_code == 200:
                            login_result = login_response.json()
                            print(f"✅ Login successful!")
                            print(f"   Welcome back: {login_result.get('user', {}).get('full_name')}")
                        else:
                            print(f"❌ Login failed: {login_response.status_code}")
                            print(f"   Error: {login_response.text}")
                    else:
                        print(f"❌ Email verification failed: {verify_response.status_code}")
                        print(f"   Error: {verify_response.text}")
                else:
                    print("❌ Invalid verification code format")
                    
            else:
                print(f"❌ Registration failed: {response.status_code}")
                error_detail = response.json() if response.content else {}
                print(f"   Error: {error_detail}")
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Backend testing completed!")


async def test_password_reset():
    """Test password reset flow"""
    print("\n5. Testing password reset...")
    
    async with httpx.AsyncClient() as client:
        # Request password reset
        reset_data = {"email": TEST_EMAIL}
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/password-reset/request",
                json=reset_data
            )
            
            if response.status_code == 200:
                print("✅ Password reset code sent to email")
                
                # Prompt for reset code
                reset_code = input("Enter the 6-digit password reset code from email: ").strip()
                new_password = "NewTestPassword123!"
                
                if reset_code and len(reset_code) == 6 and reset_code.isdigit():
                    verify_reset_data = {
                        "email": TEST_EMAIL,
                        "code": reset_code,
                        "new_password": new_password
                    }
                    
                    verify_response = await client.post(
                        f"{BASE_URL}/api/v1/auth/password-reset/verify",
                        json=verify_reset_data
                    )
                    
                    if verify_response.status_code == 200:
                        print("✅ Password reset successful!")
                    else:
                        print(f"❌ Password reset verification failed: {verify_response.status_code}")
                else:
                    print("❌ Invalid reset code format")
            else:
                print(f"❌ Password reset request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Password reset error: {e}")


if __name__ == "__main__":
    print(f"Starting backend tests at {datetime.now()}")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("Make sure PostgreSQL is running and accessible")
    print()
    
    try:
        asyncio.run(test_registration_flow())
        
        # Ask if user wants to test password reset
        test_reset = input("\nDo you want to test password reset? (y/n): ").strip().lower()
        if test_reset == 'y':
            asyncio.run(test_password_reset())
            
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
