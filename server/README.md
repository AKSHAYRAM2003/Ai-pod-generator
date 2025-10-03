# AI Podcast Generator - Backend API

A FastAPI-based backend for the AI Podcast Generator platform, providing robust authentication, user management, and API endpoints for podcast generation.

## 🚀 Features

### Authentication & User Management
- **User Registration** with email verification
- **Secure Login** with JWT tokens and refresh tokens
- **Password Reset** functionality
- **Email Verification** with secure tokens
- **User Profiles** with customizable preferences
- **Session Management** with device tracking
- **Audit Logging** for security events

### Security Features
- **Password Hashing** using bcrypt
- **JWT Tokens** with configurable expiration
- **Email Validation** and format checking
- **Rate Limiting** protection
- **CORS Configuration** for frontend integration
- **Input Validation** using Pydantic schemas

### Database & Infrastructure
- **PostgreSQL** database with SQLAlchemy ORM
- **Async Support** for high performance
- **Database Migrations** using Alembic
- **Comprehensive Testing** with pytest
- **Email Templates** with Jinja2
- **Docker Support** (coming soon)

## 📋 Requirements

- Python 3.8+
- PostgreSQL 12+
- Redis (for background tasks)
- SMTP server (for email sending)

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
cd server
chmod +x start.sh
./start.sh
```

The start script will:
- Create a virtual environment
- Install dependencies
- Copy environment configuration
- Run database migrations
- Start the development server

### 2. Environment Configuration

Update the `.env` file with your settings:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/ai_podcast_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# Frontend
FRONTEND_URL=http://localhost:3000
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb ai_podcast_db

# Run migrations
alembic upgrade head
```

### 4. Start Development Server

```bash
uvicorn main:app --reload
```

The API will be available at:
- **Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/verify-email` | Verify email address |
| POST | `/api/v1/auth/resend-verification` | Resend verification email |
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/health` | Auth service health check |

### Example: User Registration

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe"
  }'
```

### Example: User Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

## 🏗️ Project Structure

```
server/
├── app/
│   ├── api/v1/              # API routes
│   │   └── endpoints/
│   │       └── auth.py      # Authentication endpoints
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings and configuration
│   │   ├── database.py      # Database connection
│   │   ├── exceptions.py    # Custom exceptions
│   │   └── security.py      # Security utilities
│   ├── models/              # SQLAlchemy models
│   │   └── user.py          # User-related models
│   ├── schemas/             # Pydantic schemas
│   │   └── auth.py          # Authentication schemas
│   ├── services/            # Business logic
│   │   ├── auth_service.py  # Authentication service
│   │   └── email_service.py # Email service
│   └── templates/           # Email templates
│       └── emails/
├── migrations/              # Database migrations
├── tests/                   # Test suite
├── main.py                  # FastAPI application
├── requirements.txt         # Python dependencies
├── alembic.ini             # Database migration config
└── start.sh                # Setup and start script
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## 🔐 Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

### Token Management
- JWT access tokens (30 minutes default)
- Refresh tokens (7 days default)
- Device and IP tracking
- Automatic token cleanup

### Email Security
- Verification tokens expire in 24 hours
- Password reset tokens expire in 1 hour
- Secure token generation
- Rate limiting for email sending

## 📧 Email Templates

The system includes beautiful HTML email templates for:
- **Email Verification**: Welcome new users
- **Password Reset**: Secure password recovery
- **Welcome Email**: Post-verification greeting

Templates are located in `app/templates/emails/` and use Jinja2 for customization.

## 🔧 Configuration Options

### Database Settings
- `DATABASE_URL`: PostgreSQL connection string
- `DATABASE_URL_TEST`: Test database connection

### JWT Settings
- `JWT_SECRET_KEY`: Secret key for signing tokens
- `JWT_ALGORITHM`: Algorithm for JWT signing (HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Access token lifetime
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token lifetime

### Email Settings
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP server port
- `SMTP_USERNAME`: SMTP authentication username
- `SMTP_PASSWORD`: SMTP authentication password
- `SMTP_FROM_EMAIL`: Sender email address
- `SMTP_FROM_NAME`: Sender display name

### Security Settings
- `PASSWORD_MIN_LENGTH`: Minimum password length (8)
- `EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS`: Email token lifetime (24)
- `PASSWORD_RESET_TOKEN_EXPIRE_HOURS`: Reset token lifetime (1)

## 🚀 Production Deployment

### Environment Variables
Set the following for production:

```env
DEBUG=False
JWT_SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@prod-db:5432/ai_podcast_db
REDIS_URL=redis://prod-redis:6379/0
```

### Database
- Use a production PostgreSQL instance
- Run migrations: `alembic upgrade head`
- Set up regular backups

### Security
- Use HTTPS in production
- Configure proper CORS origins
- Set up rate limiting
- Monitor audit logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is part of the AI Podcast Generator platform.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/api/docs`
2. Review the test suite for examples
3. Check logs for error details
4. Verify environment configuration

---

**🎧 Ready to power amazing AI-generated podcasts!**
