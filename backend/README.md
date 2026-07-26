# RecroAI Backend API

A FastAPI-based backend with JWT authentication, SQLite database, and SQLAlchemy ORM.

## Features

-  JWT-based authentication
-  SQLite database with SQLAlchemy ORM
-  Environment-based configuration
-  Automatic API documentation (Swagger UI)
-  Password hashing with bcrypt
-  Input validation with Pydantic

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and session
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Authentication routes
│       └── users.py         # User management routes
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and update the `SECRET_KEY` with a secure random string.

4. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user information (protected)

### Users

- `GET /users/` - Get all users (protected)
- `GET /users/{user_id}` - Get user by ID (protected)

## Usage Examples

### Register a new user

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=securepassword123"
```

### Access protected endpoint

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=RecroAI API
DEBUG=True
```

## Development

The application uses:
- **FastAPI** for the web framework
- **SQLAlchemy** for ORM
- **SQLite** for the database (easily switchable to PostgreSQL/MySQL)
- **python-jose** for JWT tokens
- **passlib** for password hashing
- **pydantic** for data validation

## Production Considerations

Before deploying to production:

1. Change `SECRET_KEY` to a strong, random value
2. Set `DEBUG=False`
3. Configure CORS origins appropriately
4. Consider using PostgreSQL instead of SQLite
5. Set up proper logging
6. Add rate limiting
7. Use environment variables for sensitive data
8. Set up HTTPS

