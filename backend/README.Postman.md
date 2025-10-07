# Prism API Postman Collection

This document explains how to use the Prism API Postman collection for testing all backend endpoints.

## Overview

The Prism API Postman collection provides comprehensive testing for all backend services:
- Authentication Service
- User Management Service
- Account Management Service
- Category Management Service
- Transaction Management Service
- Budget Management Service
- Goal Management Service

## Setup Instructions

### 1. Import Collection

1. Open Postman
2. Click "Import" button
3. Select `Prism_API.postman_collection.json` from the backend directory
4. The collection will be imported with all endpoints organized by service

### 2. Environment Variables

The collection uses these environment variables:

- `base_url`: API base URL (default: http://localhost:8000)
- `access_token`: JWT access token (auto-populated after login)
- `refresh_token`: JWT refresh token (auto-populated after login)
- `user_id`: Current user ID (auto-populated after registration/login)
- `account_id`: Account ID for testing (auto-populated)
- `category_id`: Category ID for testing (auto-populated)
- `transaction_id`: Transaction ID for testing (auto-populated)
- `budget_id`: Budget ID for testing (auto-populated)
- `goal_id`: Goal ID for testing (auto-populated)

### 3. Getting Started

1. **Start the Backend**: Ensure your Django backend is running on `http://localhost:8000`
2. **Run Authentication**: Start with the Authentication folder to register/login
3. **Auto-populated Tokens**: Access tokens are automatically set after successful login
4. **Sequential Testing**: Use the folder structure to test services in logical order

## Collection Structure

### Authentication Service
- **POST** Register - Create new user account
- **POST** Login - Authenticate and get JWT tokens
- **POST** Refresh Token - Get new access token using refresh token
- **POST** Logout - Invalidate refresh token

### User Management Service
- **GET** Get User Profile - Retrieve current user details
- **PUT** Update User Profile - Update user information
- **POST** Change Password - Change user password

### Account Management Service
- **GET** List Accounts - Get all user accounts
- **POST** Create Account - Create new financial account
- **GET** Get Account Details - Get specific account details
- **PUT** Update Account - Update account information
- **DELETE** Delete Account - Remove account

### Category Management Service
- **GET** List Categories - Get all categories with hierarchy
- **POST** Create Category - Create new category
- **GET** Get Category Details - Get specific category
- **PUT** Update Category - Update category information
- **DELETE** Delete Category - Remove category

### Transaction Management Service
- **GET** List Transactions - Get all transactions with filtering
- **POST** Create Transaction - Create new transaction
- **GET** Get Transaction Details - Get specific transaction
- **PUT** Update Transaction - Update transaction information
- **DELETE** Delete Transaction - Remove transaction

### Budget Management Service
- **GET** List Budgets - Get all budgets
- **POST** Create Budget - Create new budget
- **GET** Get Budget Details - Get specific budget with spending analysis
- **PUT** Update Budget - Update budget information
- **DELETE** Delete Budget - Remove budget

### Goal Management Service
- **GET** List Goals - Get all financial goals
- **POST** Create Goal - Create new financial goal
- **GET** Get Goal Details - Get specific goal with progress
- **PUT** Update Goal - Update goal information
- **DELETE** Delete Goal - Remove goal

## Automated Tests

Each request includes automated tests that verify:

### Authentication Tests
- Registration creates user with valid data
- Login returns valid JWT tokens
- Token refresh works correctly
- Logout invalidates tokens

### CRUD Operation Tests
- POST requests return 201 status and valid data
- GET requests return 200 status and expected structure
- PUT requests return 200 status and updated data
- DELETE requests return 204 status

### Data Validation Tests
- Required fields are validated
- Data types are correct
- Relationships are properly maintained
- Error responses have correct format

### Business Logic Tests
- Budget spending calculations are accurate
- Goal progress tracking works correctly
- Account balances are updated after transactions
- Category hierarchies are maintained

## Environment Setup

### Local Development Environment
```json
{
  "base_url": "http://localhost:8000",
  "username": "testuser",
  "password": "testpass123"
}
```

### Docker Environment
```json
{
  "base_url": "http://localhost:8000",
  "username": "testuser",
  "password": "testpass123"
}
```

### Production Environment
```json
{
  "base_url": "https://your-production-domain.com",
  "username": "your_username",
  "password": "your_password"
}
```

## Testing Workflows

### Complete API Test Workflow
1. Run "Register" to create test user
2. Run "Login" to authenticate and get tokens
3. Test User Management endpoints
4. Create test account using Account Management
5. Create test categories using Category Management
6. Create test transactions using Transaction Management
7. Create test budgets using Budget Management
8. Create test goals using Goal Management

### Authentication Testing
1. Register new user
2. Login with credentials
3. Test protected endpoints with token
4. Refresh expired token
5. Logout and verify token invalidation

### Data Relationship Testing
1. Create account and categories
2. Create transactions linked to account and category
3. Create budget for specific category
4. Create goal for account
5. Verify all relationships are maintained

## Common Issues and Solutions

### Authentication Issues
- **401 Unauthorized**: Check if access token is set and valid
- **Token Expired**: Use refresh token endpoint to get new access token
- **Invalid Credentials**: Verify username/password in login request

### Data Issues
- **400 Bad Request**: Check request body format and required fields
- **404 Not Found**: Verify resource IDs exist and belong to current user
- **Foreign Key Errors**: Ensure related objects exist before creating dependencies

### Environment Issues
- **Connection Refused**: Verify backend server is running on correct port
- **CORS Errors**: Check CORS settings in Django settings
- **Database Errors**: Ensure database is running and migrations are applied

## Advanced Features

### Pre-request Scripts
- Automatically generate test data for requests
- Set dynamic values like timestamps and random numbers
- Validate environment variables are set

### Test Scripts
- Comprehensive validation of response data
- Automatic extraction of IDs for subsequent requests
- Business logic validation

### Dynamic Variables
- Auto-populated resource IDs
- Generated test data
- Environment-specific configurations

## Tips for Effective Testing

1. **Start with Authentication**: Always run authentication requests first
2. **Use Collection Runner**: Run entire folders for comprehensive testing
3. **Check Console**: Review test results in Postman console
4. **Monitor Variables**: Watch environment variables update automatically
5. **Test Edge Cases**: Try invalid data to test error handling
6. **Sequential Dependencies**: Follow the folder order for related operations

## API Documentation

For detailed API documentation, visit:
- Local: http://localhost:8000/api/docs/
- Swagger UI with interactive testing capabilities
- Complete schema definitions and examples