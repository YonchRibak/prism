# Transaction Management Service

## Overview
The Transaction Management Service handles all financial transaction operations including income, expenses, transfers, and recurring transactions in the Prism application.

## Architecture
- **Location**: `backend/prism_backend/finance/views/transaction.py`
- **URL Pattern**: `/api/finance/transactions/`
- **Authentication**: JWT Required (IsAuthenticated)
- **Serializers**: `TransactionSerializer`, `TransactionCreateSerializer`, `TransactionSummarySerializer`

## Model Structure
```python
class Transaction:
    description: str            # Transaction description
    amount: Decimal            # Transaction amount (positive=income, negative=expense)
    date: date                 # Transaction date
    account: Account           # Source account
    category: Category         # Transaction category
    notes: str                 # Optional notes
    is_recurring: bool         # Recurring transaction flag
    recurring_frequency: str   # daily, weekly, monthly, yearly
    transfer_to: Account       # Target account for transfers (optional)
    attachment: str            # File attachment path (optional)
    owner: User               # Transaction owner (foreign key)
    created_at: datetime      # Creation timestamp
    updated_at: datetime      # Last modification timestamp
```

## Endpoints

### GET /api/finance/transactions/
List all transactions for the authenticated user.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Query Parameters:**
- `account`: Filter by account ID
- `category`: Filter by category ID
- `is_recurring`: Filter by recurring status
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)
- `ordering`: Sort by fields (date, amount, created_at)
- `search`: Search in description and notes

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "description": "string",
            "amount": "decimal",
            "date": "date",
            "account": {
                "id": "integer",
                "name": "string",
                "account_type": "string"
            },
            "category": {
                "id": "integer",
                "name": "string",
                "category_type": "string"
            },
            "notes": "string",
            "is_recurring": "boolean",
            "recurring_frequency": "string",
            "transfer_to": {
                "id": "integer",
                "name": "string"
            },
            "attachment": "string",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ]
}
```

### POST /api/finance/transactions/
Create a new transaction.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "description": "string",
    "amount": "decimal",
    "date": "date",
    "account_id": "integer",
    "category_id": "integer",
    "notes": "string",
    "is_recurring": "boolean",
    "recurring_frequency": "string",
    "transfer_to_id": "integer",
    "attachment": "string"
}
```

**Response (201):**
```json
{
    "id": "integer",
    "description": "string",
    "amount": "decimal",
    "date": "date",
    "account": {
        "id": "integer",
        "name": "string",
        "account_type": "string"
    },
    "category": {
        "id": "integer",
        "name": "string",
        "category_type": "string"
    },
    "notes": "string",
    "is_recurring": "boolean",
    "recurring_frequency": "string",
    "transfer_to": {
        "id": "integer",
        "name": "string"
    },
    "attachment": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### GET /api/finance/transactions/{id}/
Retrieve a specific transaction.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Response (200):**
```json
{
    "id": "integer",
    "description": "string",
    "amount": "decimal",
    "date": "date",
    "account": {
        "id": "integer",
        "name": "string",
        "account_type": "string"
    },
    "category": {
        "id": "integer",
        "name": "string",
        "category_type": "string"
    },
    "notes": "string",
    "is_recurring": "boolean",
    "recurring_frequency": "string",
    "transfer_to": {
        "id": "integer",
        "name": "string"
    },
    "attachment": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### PUT /api/finance/transactions/{id}/
Update an existing transaction.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "description": "string",
    "amount": "decimal",
    "date": "date",
    "account_id": "integer",
    "category_id": "integer",
    "notes": "string",
    "is_recurring": "boolean",
    "recurring_frequency": "string",
    "transfer_to_id": "integer",
    "attachment": "string"
}
```

**Response (200):**
```json
{
    "id": "integer",
    "description": "string",
    "amount": "decimal",
    "date": "date",
    "account": {
        "id": "integer",
        "name": "string",
        "account_type": "string"
    },
    "category": {
        "id": "integer",
        "name": "string",
        "category_type": "string"
    },
    "notes": "string",
    "is_recurring": "boolean",
    "recurring_frequency": "string",
    "transfer_to": {
        "id": "integer",
        "name": "string"
    },
    "attachment": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### DELETE /api/finance/transactions/{id}/
Delete a transaction.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Response (204):** No content

## Custom Actions

### GET /api/finance/transactions/summary/
Get transaction summary statistics.

**Query Parameters:**
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)

**Response (200):**
```json
{
    "total_transactions": "integer",
    "total_income": "decimal",
    "total_expenses": "decimal",
    "net_income": "decimal",
    "income_transactions": "integer",
    "expense_transactions": "integer",
    "transfer_transactions": "integer"
}
```

### GET /api/finance/transactions/recent/
Get recent transactions (last 30 days).

**Query Parameters:**
- `limit`: Number of transactions to return (default: 10)

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "description": "string",
            "amount": "decimal",
            "date": "date",
            "account": {
                "id": "integer",
                "name": "string"
            },
            "category": {
                "id": "integer",
                "name": "string"
            }
        }
    ]
}
```

## Transaction Types

### Income Transactions
- **Amount**: Positive values (> 0)
- **Category Type**: Income categories
- **Examples**: Salary, freelance payment, investment returns

### Expense Transactions
- **Amount**: Negative values (< 0)
- **Category Type**: Expense categories
- **Examples**: Rent, groceries, utilities

### Transfer Transactions
- **Amount**: Can be positive or negative
- **Transfer To**: Specified target account
- **Category**: Optional (transfer categories)
- **Examples**: Moving money between accounts

## Recurring Transactions

### Frequency Options
- `daily`: Daily recurring
- `weekly`: Weekly recurring
- `monthly`: Monthly recurring
- `yearly`: Yearly recurring

### Recurring Logic
- Recurring transactions serve as templates
- Actual transactions created based on schedule
- Original recurring transaction remains for future instances

## Security Features

### Data Isolation
- Users can only access their own transactions
- All queries filtered by `owner=request.user`
- Account and category ownership validated

### Validation
- Account must belong to user
- Category must belong to user
- Transfer target account must belong to user
- Amount precision limited to 2 decimal places

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
- **Invalid account**: "Account not found or does not belong to you"
- **Invalid category**: "Category not found or does not belong to you"
- **Invalid transfer target**: "Transfer account not found or does not belong to you"
- **Invalid amount**: "Amount must be a valid decimal number"
- **Invalid date**: "Date must be in YYYY-MM-DD format"

## Dependencies
- Django REST Framework
- Django Filters
- Decimal library for financial calculations

## Related Models
- **Account**: Source and target accounts for transactions
- **Category**: Transaction categorization
- **Budget**: Transactions affect budget calculations
- **Goal**: Transactions may impact goal progress

## Business Logic

### Transaction Creation
1. Validate transaction data using `TransactionCreateSerializer`
2. Verify account and category ownership
3. Validate transfer target if specified
4. Set owner to current authenticated user
5. Create transaction record
6. Update account balance if needed

### Balance Impact
- **Income**: Increases account balance
- **Expense**: Decreases account balance
- **Transfer**: Decreases source, increases target

### Date Range Filtering
- Supports filtering by date ranges
- Efficient queries for period-based reports
- Used by budget and goal calculations

## Integration Points
- **Account Service**: Transactions update account balances
- **Category Service**: Transactions are categorized
- **Budget Service**: Transactions affect budget tracking
- **Goal Service**: Transactions may impact goal progress
- **Reporting**: Primary data source for financial reports

## Performance Considerations
- Indexed fields: `owner`, `account`, `category`, `date`, `is_recurring`
- Efficient queries for date range filtering
- Optimized summary calculations
- Bulk operations for recurring transactions

## File Attachments

### Attachment Support
- Receipts and documents can be attached
- File path stored in database
- Files stored in secure location
- Access restricted to transaction owner

### Supported Formats
- Images: JPG, PNG, GIF
- Documents: PDF, DOC, DOCX
- Maximum file size: 5MB per attachment

## Data Export

### CSV Export
- All transactions can be exported to CSV
- Includes all transaction fields
- Filtered by date range and other criteria

### API Integration
- RESTful API supports third-party integrations
- Bulk import/export capabilities
- Webhook support for real-time updates

## Testing Considerations
- Test transaction creation with various types
- Test date range filtering
- Test summary calculations
- Test recurring transaction logic
- Test transfer transaction validation
- Test file attachment handling
- Test data isolation between users
- Test balance update calculations
- Test category and account validation