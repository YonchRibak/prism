# User Management Service

## Overview
The User Management Service handles user profile operations, account settings, and user data management for authenticated users in the Prism application.

## Architecture
- **Location**: `backend/prism_backend/core/views/user.py`
- **URL Pattern**: `/api/core/user/`
- **Authentication**: JWT Required (IsAuthenticated)
- **Serializers**: `UserProfileSerializer`, `PasswordChangeSerializer`

## Endpoints

### GET /api/core/user/profile/
Retrieve the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Response (200):**
```json
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "date_joined": "datetime",
    "last_login": "datetime",
    "is_active": "boolean"
}
```

### PUT /api/core/user/profile/update/
Update the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "email": "string"
}
```

**Response (200):**
```json
{
    "message": "Profile updated successfully",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "date_joined": "datetime",
        "last_login": "datetime",
        "is_active": "boolean"
    }
}
```

**Validation:**
- Email must be unique across all users
- Username must be unique
- All fields are optional for updates

### POST /api/core/user/change-password/
Change the authenticated user's password.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "current_password": "string",
    "new_password": "string"
}
```

**Response (200):**
```json
{
    "message": "Password changed successfully"
}
```

**Validation:**
- Current password must be correct
- New password must meet Django validation requirements
- New password cannot be the same as current password

### DELETE /api/core/user/delete-account/
Permanently delete the authenticated user's account and all associated data.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "password": "string"
}
```

**Response (200):**
```json
{
    "message": "Account deleted successfully"
}
```

**⚠️ Warning**: This action is irreversible and will delete:
- User account
- All financial accounts
- All transactions
- All budgets
- All goals
- All categories

## Security Features

### Password Management
- Current password verification required for password changes
- New passwords validated against Django's password validators
- Passwords hashed using PBKDF2

### Data Protection
- Users can only access their own profile data
- Account deletion requires password confirmation
- All operations require valid JWT authentication

### Email Uniqueness
- Email addresses must be unique across the system
- Email changes validated for uniqueness

## Error Handling

### Common Error Responses
```json
{
    "error": "Error message describing the issue"
}
```

### Status Codes
- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `500`: Internal Server Error

### Specific Error Cases
- **Invalid current password**: `400` with "Current password is incorrect"
- **Email already exists**: `400` with "User with this email already exists"
- **Username already exists**: `400` with "User with this username already exists"

## Dependencies
- Django REST Framework
- Django's built-in authentication
- Custom User model

## Models Used
- **User**: Custom user model extending AbstractUser
  - `email`: Unique email address (authentication field)
  - `username`: Unique username (display name)
  - `first_name`: User's first name
  - `last_name`: User's last name
  - `date_joined`: Account creation timestamp
  - `last_login`: Last authentication timestamp
  - `is_active`: Account status

## Business Logic

### Profile Retrieval
1. Authenticate user via JWT token
2. Serialize user data using `UserProfileSerializer`
3. Return profile information

### Profile Update
1. Authenticate user via JWT token
2. Validate input data using `UserProfileSerializer`
3. Check email/username uniqueness if changed
4. Update user record
5. Return updated profile data

### Password Change
1. Authenticate user via JWT token
2. Validate current password
3. Validate new password against Django rules
4. Hash and store new password
5. Return success confirmation

### Account Deletion
1. Authenticate user via JWT token
2. Verify password for confirmation
3. Cascade delete all related financial data
4. Delete user account
5. Return deletion confirmation

## Data Relationships

### Cascading Deletions
When a user account is deleted, the following related data is automatically removed:
- `Account` records (financial accounts)
- `Category` records (transaction categories)
- `Transaction` records (financial transactions)
- `Budget` records (budget plans)
- `Goal` records (financial goals)

## Integration Points
- **Authentication Service**: Uses same User model
- **All Finance Services**: User is owner of all financial data
- **Frontend**: Profile management interface

## Validation Rules

### Email Validation
- Must be valid email format
- Must be unique across all users
- Required field

### Username Validation
- Must be unique across all users
- Alphanumeric characters and @/./+/-/_ only
- Required field

### Password Validation
- Minimum 8 characters
- Cannot be too common
- Cannot be too similar to user information
- Cannot be entirely numeric

## Testing Considerations
- Test profile retrieval for authenticated users
- Test profile updates with valid/invalid data
- Test email uniqueness validation
- Test username uniqueness validation
- Test password change with correct/incorrect current password
- Test password validation rules
- Test account deletion confirmation
- Test cascade deletion of related data
- Test authentication requirement for all endpoints