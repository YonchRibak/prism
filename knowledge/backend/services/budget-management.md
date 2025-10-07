# Budget Management Service

## Overview
The Budget Management Service handles budget creation, tracking, and monitoring for financial planning in the Prism application. It provides budget vs. actual spending analysis and alerts for overspending.

## Architecture
- **Location**: `backend/prism_backend/finance/views/budget.py`
- **URL Pattern**: `/api/finance/budgets/`
- **Authentication**: JWT Required (IsAuthenticated)
- **Serializers**: `BudgetSerializer`, `BudgetCreateSerializer`, `BudgetSummarySerializer`

## Model Structure
```python
class Budget:
    name: str                    # Budget name
    amount: Decimal             # Budget amount limit
    period: str                 # weekly, monthly, quarterly, yearly
    start_date: date            # Budget period start
    end_date: date              # Budget period end
    category: Category          # Linked category (optional)
    is_active: bool            # Budget status
    owner: User                # Budget owner (foreign key)
    created_at: datetime       # Creation timestamp
    updated_at: datetime       # Last modification timestamp

    # Calculated Properties:
    spent_amount: Decimal      # Amount spent in period
    remaining_amount: Decimal  # Amount remaining
    progress_percentage: float # Percentage of budget used
    is_over_budget: bool      # Whether budget is exceeded
```

## Endpoints

### GET /api/finance/budgets/
List all budgets for the authenticated user.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Query Parameters:**
- `category`: Filter by category ID
- `period`: Filter by budget period
- `is_active`: Filter by active status
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)
- `ordering`: Sort by fields (name, amount, start_date, created_at)
- `search`: Search in budget name

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "amount": "decimal",
            "period": "string",
            "period_display": "string",
            "start_date": "date",
            "end_date": "date",
            "category": {
                "id": "integer",
                "name": "string",
                "category_type": "string"
            },
            "is_active": "boolean",
            "spent_amount": "decimal",
            "remaining_amount": "decimal",
            "progress_percentage": "float",
            "is_over_budget": "boolean",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ]
}
```

### POST /api/finance/budgets/
Create a new budget.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "name": "string",
    "amount": "decimal",
    "period": "string",
    "start_date": "date",
    "end_date": "date",
    "category_id": "integer",
    "is_active": "boolean"
}
```

**Response (201):**
```json
{
    "id": "integer",
    "name": "string",
    "amount": "decimal",
    "period": "string",
    "period_display": "string",
    "start_date": "date",
    "end_date": "date",
    "category": {
        "id": "integer",
        "name": "string",
        "category_type": "string"
    },
    "is_active": "boolean",
    "spent_amount": "0.00",
    "remaining_amount": "decimal",
    "progress_percentage": 0.0,
    "is_over_budget": false,
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### GET /api/finance/budgets/{id}/
Retrieve a specific budget.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Response (200):**
```json
{
    "id": "integer",
    "name": "string",
    "amount": "decimal",
    "period": "string",
    "period_display": "string",
    "start_date": "date",
    "end_date": "date",
    "category": {
        "id": "integer",
        "name": "string",
        "category_type": "string"
    },
    "is_active": "boolean",
    "spent_amount": "decimal",
    "remaining_amount": "decimal",
    "progress_percentage": "float",
    "is_over_budget": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### PUT /api/finance/budgets/{id}/
Update an existing budget.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "name": "string",
    "amount": "decimal",
    "period": "string",
    "start_date": "date",
    "end_date": "date",
    "category_id": "integer",
    "is_active": "boolean"
}
```

**Response (200):**
```json
{
    "id": "integer",
    "name": "string",
    "amount": "decimal",
    "period": "string",
    "period_display": "string",
    "start_date": "date",
    "end_date": "date",
    "category": {
        "id": "integer",
        "name": "string",
        "category_type": "string"
    },
    "is_active": "boolean",
    "spent_amount": "decimal",
    "remaining_amount": "decimal",
    "progress_percentage": "float",
    "is_over_budget": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### DELETE /api/finance/budgets/{id}/
Delete a budget.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Response (204):** No content

## Custom Actions

### GET /api/finance/budgets/current/
Get current active budgets (within date range).

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "amount": "decimal",
            "period": "string",
            "spent_amount": "decimal",
            "remaining_amount": "decimal",
            "progress_percentage": "float",
            "is_over_budget": "boolean",
            "category": {
                "id": "integer",
                "name": "string"
            }
        }
    ]
}
```

### GET /api/finance/budgets/over_budget/
Get budgets that are over their limit.

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "amount": "decimal",
            "spent_amount": "decimal",
            "over_amount": "decimal",
            "progress_percentage": "float",
            "category": {
                "id": "integer",
                "name": "string"
            }
        }
    ]
}
```

### GET /api/finance/budgets/summary/
Get budget summary statistics.

**Response (200):**
```json
{
    "total_budgets": "integer",
    "total_budget_amount": "decimal",
    "total_spent": "decimal",
    "total_remaining": "decimal",
    "over_budget_count": "integer",
    "on_track_count": "integer"
}
```

## Budget Periods

### Supported Periods
- `weekly`: Weekly budget (7 days)
- `monthly`: Monthly budget (calendar month)
- `quarterly`: Quarterly budget (3 months)
- `yearly`: Yearly budget (12 months)

### Period Calculation
- **Weekly**: Start date to start date + 7 days
- **Monthly**: First day of month to last day of month
- **Quarterly**: First day of quarter to last day of quarter
- **Yearly**: First day of year to last day of year

## Budget Tracking

### Spent Amount Calculation
- Aggregates all expense transactions within budget period
- Filters by budget category if specified
- Excludes income and transfer transactions
- Real-time calculation based on transaction data

### Progress Monitoring
- **Progress Percentage**: (spent_amount / budget_amount) * 100
- **Remaining Amount**: budget_amount - spent_amount
- **Over Budget**: spent_amount > budget_amount

### Category Linking
- Budgets can be linked to specific categories
- Spending tracked only for linked category
- General budgets track all spending if no category

## Security Features

### Data Isolation
- Users can only access their own budgets
- All queries filtered by `owner=request.user`
- Category must belong to user if specified

### Validation
- Budget amount must be positive
- Start date must be before end date
- Category must belong to user
- Period dates must be consistent

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
- **Invalid amount**: "Budget amount must be positive"
- **Invalid dates**: "Start date must be before end date"
- **Invalid category**: "Category not found or does not belong to you"
- **Duplicate name**: "Budget with this name already exists"

## Dependencies
- Django REST Framework
- Django Filters
- Decimal library for financial calculations

## Related Models
- **Category**: Budgets can be linked to categories
- **Transaction**: Transactions used to calculate spending
- **User**: Budget ownership

## Business Logic

### Budget Creation
1. Validate budget data using `BudgetCreateSerializer`
2. Verify category ownership if specified
3. Set owner to current authenticated user
4. Calculate initial spent amount
5. Create budget record

### Spending Calculation
1. Query transactions within budget period
2. Filter by budget category if specified
3. Sum expense transaction amounts
4. Update calculated fields (remaining, progress, over_budget)

### Period Management
- Automatic period boundary calculation
- Support for overlapping budgets
- Historical budget tracking

## Integration Points
- **Transaction Service**: Spending calculated from transactions
- **Category Service**: Budgets can be category-specific
- **Reporting**: Budget vs. actual reports
- **Notifications**: Overspending alerts

## Performance Considerations
- Indexed fields: `owner`, `category`, `is_active`, `start_date`, `end_date`
- Cached spending calculations
- Efficient transaction aggregation queries
- Optimized period filtering

## Budget Templates

### Common Budget Types
- **Monthly Expense Budgets**: Rent, groceries, utilities
- **Category Budgets**: Entertainment, dining, shopping
- **Savings Budgets**: Emergency fund, vacation fund
- **Debt Payment Budgets**: Credit card, loan payments

### Auto-Generated Budgets
- Based on spending history
- Category-based recommendations
- Seasonal budget adjustments

## Notifications and Alerts

### Budget Alerts
- 80% of budget reached
- 100% of budget reached (over budget)
- Monthly budget summary
- Weekly spending updates

### Alert Delivery
- In-app notifications
- Email notifications
- Push notifications (mobile)

## Reporting Features

### Budget Reports
- Budget vs. actual spending
- Variance analysis
- Historical budget performance
- Category-wise budget tracking

### Export Options
- CSV export of budget data
- PDF budget reports
- Integration with accounting software

## Testing Considerations
- Test budget creation with various periods
- Test spending calculation accuracy
- Test over-budget detection
- Test category-specific budgets
- Test date range validation
- Test summary calculations
- Test data isolation between users
- Test period boundary calculations
- Test historical budget tracking