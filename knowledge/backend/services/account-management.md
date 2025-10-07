# Account Management Service

## Overview
The Account Management Service handles financial account operations including bank accounts, credit cards, investment accounts, and cash accounts for users in the Prism application.

## Architecture
- **Location**: `backend/prism_backend/finance/views/account.py`
- **URL Pattern**: `/api/finance/accounts/`
- **Authentication**: JWT Required (IsAuthenticated)
- **Serializers**: `AccountSerializer`, `AccountCreateSerializer`, `AccountSummarySerializer`

## Model Structure
```python
class Account:
    name: str                    # Account display name
    account_type: str           # checking, savings, credit, investment, cash
    account_number: str         # Masked account number (optional)
    balance: Decimal            # Current account balance
    currency: str               # Currency code (default: USD)
    is_active: bool            # Account status
    owner: User                # Account owner (foreign key)
    created_at: datetime       # Creation timestamp
    updated_at: datetime       # Last modification timestamp
```

## Endpoints

### GET /api/finance/accounts/
List all accounts for the authenticated user.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Query Parameters:**
- `account_type`: Filter by account type
- `is_active`: Filter by active status
- `ordering`: Sort by fields (name, balance, created_at)
- `search`: Search in name and account_number

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "account_type": "string",
            "account_type_display": "string",
            "account_number": "string",
            "balance": "decimal",
            "currency": "string",
            "is_active": "boolean",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ]
}
```

### POST /api/finance/accounts/
Create a new financial account.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "name": "string",
    "account_type": "string",
    "account_number": "string",
    "balance": "decimal",
    "currency": "string",
    "is_active": "boolean"
}
```

**Response (201):**
```json
{
    "id": "integer",
    "name": "string",
    "account_type": "string",
    "account_type_display": "string",
    "account_number": "string",
    "balance": "decimal",
    "currency": "string",
    "is_active": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### GET /api/finance/accounts/{id}/
Retrieve a specific account.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Response (200):**
```json
{
    "id": "integer",
    "name": "string",
    "account_type": "string",
    "account_type_display": "string",
    "account_number": "string",
    "balance": "decimal",
    "currency": "string",
    "is_active": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### PUT /api/finance/accounts/{id}/
Update an existing account.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "name": "string",
    "account_type": "string",
    "account_number": "string",
    "balance": "decimal",
    "currency": "string",
    "is_active": "boolean"
}
```

**Response (200):**
```json
{
    "id": "integer",
    "name": "string",
    "account_type": "string",
    "account_type_display": "string",
    "account_number": "string",
    "balance": "decimal",
    "currency": "string",
    "is_active": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### DELETE /api/finance/accounts/{id}/
Delete an account (soft delete by setting inactive).

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Response (204):** No content

## Custom Actions

### GET /api/finance/accounts/active/
Get only active accounts.

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "account_type": "string",
            "balance": "decimal",
            "currency": "string"
        }
    ]
}
```

### GET /api/finance/accounts/by_type/
Get accounts grouped by type.

**Response (200):**
```json
{
    "checking": {
        "count": "integer",
        "total_balance": "decimal",
        "accounts": [...]
    },
    "savings": {
        "count": "integer",
        "total_balance": "decimal",
        "accounts": [...]
    },
    "credit": {
        "count": "integer",
        "total_balance": "decimal",
        "accounts": [...]
    },
    "investment": {
        "count": "integer",
        "total_balance": "decimal",
        "accounts": [...]
    },
    "cash": {
        "count": "integer",
        "total_balance": "decimal",
        "accounts": [...]
    }
}
```

### GET /api/finance/accounts/summary/
Get account summary statistics.

**Response (200):**
```json
{
    "total_accounts": "integer",
    "active_accounts": "integer",
    "total_balance": "decimal",
    "balance_by_type": {
        "checking": "decimal",
        "savings": "decimal",
        "credit": "decimal",
        "investment": "decimal",
        "cash": "decimal"
    },
    "net_worth": "decimal"
}
```

### POST /api/finance/accounts/{id}/update_balance/
Update account balance directly.

**Request Body:**
```json
{
    "balance": "decimal"
}
```

**Response (200):**
```json
{
    "id": "integer",
    "name": "string",
    "balance": "decimal",
    "previous_balance": "decimal",
    "updated_at": "datetime"
}
```

## Account Types

### Supported Types
- `checking`: Checking Account
- `savings`: Savings Account
- `credit`: Credit Card
- `investment`: Investment Account
- `cash`: Cash Account

### Type-Specific Behavior
- **Credit accounts**: Negative balances represent debt
- **Investment accounts**: Can have fluctuating balances
- **Cash accounts**: Typically small positive balances

## Security Features

### Data Isolation
- Users can only access their own accounts
- All queries filtered by `owner=request.user`
- Account creation automatically assigns current user as owner

### Validation
- Account names must be unique per user
- Balance precision limited to 2 decimal places
- Currency codes validated (3-letter ISO codes)

## Error Handling

### Common Error Responses
```json
{
    "error": "Error message describing the issue"
}
```

### Status Codes
- `200`: Success
- `201`: Created
- `204`: No Content (deletion)
- `400`: Bad Request (validation errors)
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

### Specific Validation Errors
- **Duplicate account name**: "Account with this name already exists"
- **Invalid currency**: "Enter a valid 3-letter currency code"
- **Invalid balance**: "Balance must be a valid decimal number"

## Dependencies
- Django REST Framework
- Django Filters
- Decimal library for financial calculations

## Related Models
- **Transaction**: Transactions reference accounts
- **Budget**: Budgets can be linked to accounts
- **Goal**: Goals can be linked to accounts

## Business Logic

### Account Creation
1. Validate account data using `AccountCreateSerializer`
2. Set owner to current authenticated user
3. Create account record
4. Return account data using `AccountSerializer`

### Balance Updates
1. Validate new balance value
2. Store previous balance for audit
3. Update balance with timestamp
4. Return updated account data

### Account Deletion
- Soft delete: Sets `is_active = False`
- Preserves transaction history
- Account remains in database for data integrity

## Integration Points
- **Transaction Service**: Accounts used in transaction records
- **Budget Service**: Budgets can be linked to specific accounts
- **Goal Service**: Goals can be linked to accounts for tracking
- **Reporting**: Account balances used in financial reports

## Performance Considerations
- Indexed fields: `owner`, `account_type`, `is_active`
- Balance calculations cached in account record
- Efficient queries for account summaries

## Testing Considerations
- Test account creation with various types
- Test balance updates and validation
- Test account type filtering
- Test summary calculations
- Test data isolation between users
- Test soft deletion behavior
- Test duplicate name validation per user