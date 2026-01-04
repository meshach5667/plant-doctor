# Plant Doctor API

A production-ready FastAPI backend for AI-powered plant disease diagnosis.

## Features

- 🌱 **AI Disease Diagnosis**: Upload plant images for instant disease detection
- 🔐 **JWT Authentication**: Secure authentication with access and refresh tokens
- 👨‍🌾 **Farm Management**: Track crops and their health status
- 📅 **Routine Checks**: Automated care reminders for your plants
- 🛡️ **Production Ready**: Rate limiting, security headers, logging, and error handling

## Project Structure

```
server/
├── core/                   # Core utilities and middleware
│   ├── __init__.py
│   ├── exceptions.py       # Custom exception classes
│   ├── handlers.py         # Exception handlers
│   ├── middleware.py       # Request logging, rate limiting
│   └── security.py         # JWT and password utilities
├── models/                 # SQLAlchemy database models
│   └── __init__.py
├── routes/                 # API route handlers
│   ├── __init__.py
│   ├── auth.py            # Authentication endpoints
│   ├── dependencies.py    # Dependency injection
│   ├── diagnosis.py       # Disease diagnosis endpoints
│   ├── farm.py            # Farm management endpoints
│   └── routines.py        # Routine check endpoints
├── schemas/               # Pydantic request/response schemas
│   ├── __init__.py
│   ├── diagnosis.py
│   ├── plant.py
│   ├── routine.py
│   └── user.py
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py
│   ├── diagnosis_service.py
│   ├── disease_data.py
│   └── routine_service.py
├── model/                 # ML model files
├── uploads/               # Uploaded images
├── config.py              # Application configuration
├── database.py            # Database setup
├── main.py                # Application entry point
└── utils.py               # Utility functions
```

## Quick Start

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

**Important**: Generate a secure secret key for production:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 4. Run the Server

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

When running in development mode, API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

The API uses JWT Bearer token authentication.

### Register a New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Using the Token

Include the access token in the Authorization header:

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Refresh Token

When the access token expires, use the refresh token to get a new one:

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

## Configuration

All configuration is done via environment variables. See `.env.example` for available options.

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (required in production) | Random |
| `DATABASE_URL` | Database connection string | SQLite |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | 7 |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Rate limit per IP | 60 |
| `DEBUG` | Enable debug mode | false |
| `ENVIRONMENT` | development/staging/production | development |

## Security Features

- **JWT Authentication**: Short-lived access tokens with refresh token rotation
- **Password Hashing**: bcrypt with configurable rounds
- **Rate Limiting**: Per-IP request limiting
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, HSTS, etc.
- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic schema validation on all inputs
- **Error Handling**: Consistent error responses without exposing internals

## Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "model_loaded": true
}
```

## License

MIT License