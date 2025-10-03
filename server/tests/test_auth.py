import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import AuthService
from app.schemas.auth import UserRegistrationRequest


class TestUserRegistration:
    """Test user registration functionality"""
    
    async def test_register_user_success(self, async_client: AsyncClient):
        """Test successful user registration"""
        registration_data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=registration_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Registration successful. Please check your email to verify your account."
        assert data["email"] == "test@example.com"
        assert data["verification_required"] is True
        assert "user_id" in data
    
    async def test_register_user_duplicate_email(self, async_client: AsyncClient):
        """Test registration with duplicate email"""
        registration_data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        # First registration
        response1 = await async_client.post("/api/v1/auth/register", json=registration_data)
        assert response1.status_code == 201
        
        # Second registration with same email
        response2 = await async_client.post("/api/v1/auth/register", json=registration_data)
        assert response2.status_code == 409
        data = response2.json()
        assert "Email already registered" in data["detail"]["detail"]
    
    async def test_register_user_weak_password(self, async_client: AsyncClient):
        """Test registration with weak password"""
        registration_data = {
            "email": "test2@example.com",
            "password": "weak",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 400
        data = response.json()
        assert "password" in data["detail"]["detail"].lower()
    
    async def test_register_user_invalid_email(self, async_client: AsyncClient):
        """Test registration with invalid email"""
        registration_data = {
            "email": "invalid-email",
            "password": "TestPass123!",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 422  # Pydantic validation error
    
    async def test_register_user_missing_fields(self, async_client: AsyncClient):
        """Test registration with missing required fields"""
        registration_data = {
            "email": "test3@example.com",
            "password": "TestPass123!"
            # Missing first_name and last_name
        }
        
        response = await async_client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 422  # Pydantic validation error


class TestEmailVerification:
    """Test email verification functionality"""
    
    async def test_verify_email_invalid_token(self, async_client: AsyncClient):
        """Test email verification with invalid token"""
        verification_data = {
            "token": "invalid-token"
        }
        
        response = await async_client.post("/api/v1/auth/verify-email", json=verification_data)
        assert response.status_code == 404
        data = response.json()
        assert "token" in data["detail"]["detail"].lower()


class TestUserLogin:
    """Test user login functionality"""
    
    async def test_login_unverified_user(self, async_client: AsyncClient, db_session: AsyncSession):
        """Test login with unverified user"""
        # First register a user
        registration_data = {
            "email": "unverified@example.com",
            "password": "TestPass123!",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        register_response = await async_client.post("/api/v1/auth/register", json=registration_data)
        assert register_response.status_code == 201
        
        # Try to login without verification
        login_data = {
            "email": "unverified@example.com",
            "password": "TestPass123!"
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        data = response.json()
        assert "verify" in data["detail"]["detail"].lower()
    
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPass123!"
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"]["detail"].lower()


class TestHealthCheck:
    """Test API health check"""
    
    async def test_main_health_check(self, async_client: AsyncClient):
        """Test main health check endpoint"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    async def test_auth_health_check(self, async_client: AsyncClient):
        """Test auth service health check endpoint"""
        response = await async_client.get("/api/v1/auth/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "authentication"
