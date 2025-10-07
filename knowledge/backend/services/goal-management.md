# Goal Management Service

## Overview
The Goal Management Service handles financial goal creation, tracking, and progress monitoring for long-term financial planning in the Prism application. It supports various goal types including savings, debt payoff, and investment targets.

## Architecture
- **Location**: `backend/prism_backend/finance/views/goal.py`
- **URL Pattern**: `/api/finance/goals/`
- **Authentication**: JWT Required (IsAuthenticated)
- **Serializers**: `GoalSerializer`, `GoalCreateSerializer`, `GoalProgressUpdateSerializer`, `GoalSummarySerializer`

## Model Structure
```python
class Goal:
    name: str                    # Goal name
    description: str            # Goal description
    goal_type: str              # savings, debt, investment, purchase
    target_amount: Decimal      # Target amount to reach
    current_amount: Decimal     # Current amount saved/paid
    target_date: date           # Target completion date (optional)
    linked_account: Account     # Linked account for tracking (optional)
    is_active: bool            # Goal status
    is_completed: bool          # Completion status
    completed_at: datetime      # Completion timestamp (optional)
    owner: User                # Goal owner (foreign key)
    created_at: datetime       # Creation timestamp
    updated_at: datetime       # Last modification timestamp

    # Calculated Properties:
    remaining_amount: Decimal   # Amount remaining to target
    progress_percentage: float  # Percentage of goal completed
    is_goal_reached: bool      # Whether target amount is reached
```

## Endpoints

### GET /api/finance/goals/
List all goals for the authenticated user.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Query Parameters:**
- `goal_type`: Filter by goal type
- `is_active`: Filter by active status
- `is_completed`: Filter by completion status
- `linked_account`: Filter by linked account ID
- `ordering`: Sort by fields (name, target_amount, target_date, created_at)
- `search`: Search in name and description

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "description": "string",
            "goal_type": "string",
            "goal_type_display": "string",
            "target_amount": "decimal",
            "current_amount": "decimal",
            "remaining_amount": "decimal",
            "progress_percentage": "float",
            "target_date": "date",
            "linked_account": {
                "id": "integer",
                "name": "string"
            },
            "linked_account_name": "string",
            "is_active": "boolean",
            "is_completed": "boolean",
            "is_goal_reached": "boolean",
            "completed_at": "datetime",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ]
}
```

### POST /api/finance/goals/
Create a new goal.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "name": "string",
    "description": "string",
    "goal_type": "string",
    "target_amount": "decimal",
    "current_amount": "decimal",
    "target_date": "date",
    "linked_account_id": "integer",
    "is_active": "boolean"
}
```

**Response (201):**
```json
{
    "id": "integer",
    "name": "string",
    "description": "string",
    "goal_type": "string",
    "goal_type_display": "string",
    "target_amount": "decimal",
    "current_amount": "decimal",
    "remaining_amount": "decimal",
    "progress_percentage": "float",
    "target_date": "date",
    "linked_account": {
        "id": "integer",
        "name": "string"
    },
    "linked_account_name": "string",
    "is_active": "boolean",
    "is_completed": false,
    "is_goal_reached": "boolean",
    "completed_at": null,
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### GET /api/finance/goals/{id}/
Retrieve a specific goal.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Response (200):**
```json
{
    "id": "integer",
    "name": "string",
    "description": "string",
    "goal_type": "string",
    "goal_type_display": "string",
    "target_amount": "decimal",
    "current_amount": "decimal",
    "remaining_amount": "decimal",
    "progress_percentage": "float",
    "target_date": "date",
    "linked_account": {
        "id": "integer",
        "name": "string"
    },
    "linked_account_name": "string",
    "is_active": "boolean",
    "is_completed": "boolean",
    "is_goal_reached": "boolean",
    "completed_at": "datetime",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### PUT /api/finance/goals/{id}/
Update an existing goal.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "name": "string",
    "description": "string",
    "goal_type": "string",
    "target_amount": "decimal",
    "current_amount": "decimal",
    "target_date": "date",
    "linked_account_id": "integer",
    "is_active": "boolean"
}
```

**Response (200):**
```json
{
    "id": "integer",
    "name": "string",
    "description": "string",
    "goal_type": "string",
    "goal_type_display": "string",
    "target_amount": "decimal",
    "current_amount": "decimal",
    "remaining_amount": "decimal",
    "progress_percentage": "float",
    "target_date": "date",
    "linked_account": {
        "id": "integer",
        "name": "string"
    },
    "linked_account_name": "string",
    "is_active": "boolean",
    "is_completed": "boolean",
    "is_goal_reached": "boolean",
    "completed_at": "datetime",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### DELETE /api/finance/goals/{id}/
Delete a goal.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Response (204):** No content

## Custom Actions

### POST /api/finance/goals/{id}/update_progress/
Update goal progress by adding/subtracting amount.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "amount": "decimal"
}
```

**Response (200):**
```json
{
    "id": "integer",
    "name": "string",
    "target_amount": "decimal",
    "current_amount": "decimal",
    "remaining_amount": "decimal",
    "progress_percentage": "float",
    "is_goal_reached": "boolean",
    "is_completed": "boolean",
    "updated_at": "datetime"
}
```

### GET /api/finance/goals/active/
Get active goals (not completed).

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "target_amount": "decimal",
            "current_amount": "decimal",
            "progress_percentage": "float",
            "target_date": "date",
            "goal_type": "string"
        }
    ]
}
```

### GET /api/finance/goals/completed/
Get completed goals.

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "target_amount": "decimal",
            "current_amount": "decimal",
            "completed_at": "datetime",
            "goal_type": "string"
        }
    ]
}
```

### GET /api/finance/goals/near_target/
Get goals that are close to their target (>80% progress).

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "target_amount": "decimal",
            "current_amount": "decimal",
            "progress_percentage": "float",
            "remaining_amount": "decimal"
        }
    ]
}
```

### GET /api/finance/goals/summary/
Get goal summary statistics.

**Response (200):**
```json
{
    "total_goals": "integer",
    "active_goals": "integer",
    "completed_goals": "integer",
    "total_target_amount": "decimal",
    "total_saved_amount": "decimal",
    "total_remaining_amount": "decimal",
    "average_progress": "float",
    "by_type": {
        "savings": {
            "count": "integer",
            "target_amount": "decimal",
            "saved_amount": "decimal"
        },
        "debt": {
            "count": "integer",
            "target_amount": "decimal",
            "saved_amount": "decimal"
        },
        "investment": {
            "count": "integer",
            "target_amount": "decimal",
            "saved_amount": "decimal"
        },
        "purchase": {
            "count": "integer",
            "target_amount": "decimal",
            "saved_amount": "decimal"
        }
    }
}
```

## Goal Types

### Supported Types
- `savings`: Savings Goal (emergency fund, vacation, etc.)
- `debt`: Debt Payoff Goal (credit card, loan, etc.)
- `investment`: Investment Goal (retirement, portfolio, etc.)
- `purchase`: Purchase Goal (car, house, gadget, etc.)

### Type-Specific Behavior
- **Savings Goals**: Current amount represents money saved
- **Debt Goals**: Current amount represents amount paid toward debt
- **Investment Goals**: Current amount represents investment value
- **Purchase Goals**: Current amount represents money saved for purchase

## Progress Tracking

### Progress Calculation
- **Progress Percentage**: (current_amount / target_amount) * 100
- **Remaining Amount**: target_amount - current_amount
- **Goal Reached**: current_amount >= target_amount

### Automatic Completion
- Goals automatically marked as completed when target reached
- Completion timestamp recorded
- Option to continue tracking beyond target

### Manual Progress Updates
- Direct amount adjustments via API
- Positive amounts increase progress
- Negative amounts decrease progress (corrections)

## Account Linking

### Linked Account Benefits
- Automatic progress tracking based on account balance
- Real-time goal updates
- Integration with transaction history

### Account Sync
- Periodic sync with linked account balance
- Manual sync triggers available
- Historical progress tracking

## Security Features

### Data Isolation
- Users can only access their own goals
- All queries filtered by `owner=request.user`
- Linked account must belong to user

### Validation
- Target amount must be positive
- Current amount cannot be negative
- Linked account ownership verified
- Progress updates validated for reasonable amounts

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
- **Invalid target amount**: "Target amount must be positive"
- **Invalid current amount**: "Current amount cannot be negative"
- **Invalid linked account**: "Account not found or does not belong to you"
- **Invalid progress update**: "Progress update would result in negative amount"

## Dependencies
- Django REST Framework
- Django Filters
- Decimal library for financial calculations

## Related Models
- **Account**: Goals can be linked to accounts
- **Transaction**: Transactions may affect goal progress
- **User**: Goal ownership

## Business Logic

### Goal Creation
1. Validate goal data using `GoalCreateSerializer`
2. Verify linked account ownership if specified
3. Set owner to current authenticated user
4. Calculate initial progress metrics
5. Create goal record

### Progress Updates
1. Validate progress change amount
2. Update current amount
3. Recalculate progress metrics
4. Check for goal completion
5. Update completion status if reached

### Automatic Completion
- Check if current_amount >= target_amount
- Set is_completed = True
- Record completed_at timestamp
- Trigger completion notifications

## Integration Points
- **Account Service**: Goals can be linked to accounts
- **Transaction Service**: Transactions may update goal progress
- **Notification Service**: Goal completion and milestone alerts
- **Reporting**: Goal progress reports and analytics

## Performance Considerations
- Indexed fields: `owner`, `goal_type`, `is_active`, `is_completed`, `target_date`
- Cached progress calculations
- Efficient summary queries
- Optimized account sync operations

## Goal Templates

### Common Goal Templates
- **Emergency Fund**: 3-6 months of expenses
- **Vacation Fund**: Based on destination and duration
- **Car Purchase**: Down payment + taxes
- **House Down Payment**: 10-20% of home value
- **Retirement**: Age-based target amounts

### Smart Suggestions
- Goals based on spending patterns
- Industry-standard targets
- Peer comparison insights

## Notifications and Milestones

### Milestone Alerts
- 25%, 50%, 75% progress reached
- Goal completion
- Target date approaching
- Monthly/weekly progress updates

### Motivation Features
- Visual progress indicators
- Achievement badges
- Progress sharing options
- Goal streak tracking

## Reporting Features

### Goal Reports
- Progress over time
- Goal completion rates
- Target vs. actual timeline
- Goal category analysis

### Export Options
- CSV export of goal data
- PDF progress reports
- Integration with financial planning tools

## Testing Considerations
- Test goal creation with various types
- Test progress calculation accuracy
- Test automatic completion logic
- Test linked account validation
- Test progress update validation
- Test summary calculations
- Test data isolation between users
- Test milestone detection
- Test target date handling
- Test negative progress scenarios