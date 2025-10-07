# Authentication Service

## Overview
The Authentication Service handles user registration, login, and JWT token management for the Prism financial management application.

## Architecture
- **Location**: `backend/prism_backend/core/views/auth.py`
- **URL Pattern**: `/api/core/auth/`
- **Authentication**: None required (public endpoints)
- **Serializers**: `UserRegistrationSerializer`, `UserSerializer`

## Endpoints

### POST /api/core/auth/register/
Register a new user account.

**Request Body:**
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "first_name": "string",
    "last_name": "string"
}
```

**Response (201):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "date_joined": "datetime"
    },
    "tokens": {
        "access": "jwt_token",
        "refresh": "jwt_token"
    }
}
```

**Validation:**
- Email must be unique
- Password must meet Django validation requirements
- All fields are required

### POST /api/core/auth/login/
Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
    "email": "string",
    "password": "string"
}
```

**Response (200):**
```json
{
    "message": "Login successful",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "first_name": "string",
        "last_name": "string"
    },
    "tokens": {
        "access": "jwt_token",
        "refresh": "jwt_token"
    }
}
```

**Error Responses:**
- `400`: Invalid credentials
- `401`: Account inactive

### POST /api/core/auth/refresh/
Refresh JWT access token using refresh token.

**Request Body:**
```json
{
    "refresh": "jwt_refresh_token"
}
```

**Response (200):**
```json
{
    "access": "new_jwt_access_token"
}
```

## Security Features

### JWT Token Configuration
- **Access Token Lifetime**: Configurable (default: 1 hour)
- **Refresh Token Lifetime**: Configurable (default: 7 days)
- **Algorithm**: HS256
- **Issuer**: Prism Backend

### Password Security
- Django's built-in password validation
- Passwords are hashed using PBKDF2
- Minimum complexity requirements enforced

### Email-based Authentication
- Users authenticate with email instead of username
- Email uniqueness enforced at database level

## Error Handling

### Common Error Responses
```json
{
    "error": "Error message describing the issue"
}
```

### Status Codes
- `200`: Success
- `201`: Created (registration)
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid credentials)
- `500`: Internal Server Error

## Dependencies
- Django REST Framework
- djangorestframework-simplejwt
- Django's built-in User model (extended)

## Models Used
- **User**: Custom user model extending AbstractUser
  - `email`: Primary authentication field
  - `username`: Display name
  - `first_name`, `last_name`: User profile data

## Business Logic

### Registration Process
1. Validate input data using `UserRegistrationSerializer`
2. Check email uniqueness
3. Hash password using Django's password hashers
4. Create user record
5. Generate JWT tokens
6. Return user data and tokens

### Login Process
1. Validate email and password
2. Authenticate against Django's authentication backend
3. Check if user account is active
4. Generate fresh JWT tokens
5. Return user data and tokens

### Token Refresh Process
1. Validate refresh token
2. Generate new access token
3. Return new access token

## Integration Points
- **User Management Service**: Shares User model
- **All Finance Services**: Tokens used for authentication
- **Frontend**: Receives and manages JWT tokens

## Configuration
Located in `settings.py`:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

## Testing Considerations
- Test registration with various email formats
- Test password validation rules
- Test token expiration scenarios
- Test invalid credentials handling
- Test account activation status