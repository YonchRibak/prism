# Category Management Service

## Overview
The Category Management Service handles transaction categorization, providing hierarchical category structures for organizing income and expense transactions in the Prism application.

## Architecture
- **Location**: `backend/prism_backend/finance/views/category.py`
- **URL Pattern**: `/api/finance/categories/`
- **Authentication**: JWT Required (IsAuthenticated)
- **Serializers**: `CategorySerializer`, `CategoryTreeSerializer`

## Model Structure
```python
class Category:
    name: str                    # Category name
    category_type: str          # 'income' or 'expense'
    description: str            # Optional description
    parent: Category            # Parent category (for subcategories)
    color: str                  # Hex color code for UI
    icon: str                   # Icon identifier
    is_active: bool            # Category status
    owner: User                # Category owner (foreign key)
    created_at: datetime       # Creation timestamp
    updated_at: datetime       # Last modification timestamp
```

## Endpoints

### GET /api/finance/categories/
List all categories for the authenticated user.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Query Parameters:**
- `category_type`: Filter by type (income/expense)
- `is_active`: Filter by active status
- `parent`: Filter by parent category ID
- `ordering`: Sort by fields (name, created_at)
- `search`: Search in category name

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "category_type": "string",
            "category_type_display": "string",
            "description": "string",
            "parent": "integer",
            "parent_name": "string",
            "color": "string",
            "icon": "string",
            "is_active": "boolean",
            "subcategory_count": "integer",
            "transaction_count": "integer",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ]
}
```

### POST /api/finance/categories/
Create a new category.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "name": "string",
    "category_type": "string",
    "description": "string",
    "parent": "integer",
    "color": "string",
    "icon": "string",
    "is_active": "boolean"
}
```

**Response (201):**
```json
{
    "id": "integer",
    "name": "string",
    "category_type": "string",
    "category_type_display": "string",
    "description": "string",
    "parent": "integer",
    "parent_name": "string",
    "color": "string",
    "icon": "string",
    "is_active": "boolean",
    "subcategory_count": 0,
    "transaction_count": 0,
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### GET /api/finance/categories/{id}/
Retrieve a specific category.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Response (200):**
```json
{
    "id": "integer",
    "name": "string",
    "category_type": "string",
    "category_type_display": "string",
    "description": "string",
    "parent": "integer",
    "parent_name": "string",
    "color": "string",
    "icon": "string",
    "is_active": "boolean",
    "subcategory_count": "integer",
    "transaction_count": "integer",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### PUT /api/finance/categories/{id}/
Update an existing category.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Request Body:**
```json
{
    "name": "string",
    "category_type": "string",
    "description": "string",
    "parent": "integer",
    "color": "string",
    "icon": "string",
    "is_active": "boolean"
}
```

**Response (200):**
```json
{
    "id": "integer",
    "name": "string",
    "category_type": "string",
    "category_type_display": "string",
    "description": "string",
    "parent": "integer",
    "parent_name": "string",
    "color": "string",
    "icon": "string",
    "is_active": "boolean",
    "subcategory_count": "integer",
    "transaction_count": "integer",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### DELETE /api/finance/categories/{id}/
Delete a category with validation.

**Headers:**
```
Authorization: Bearer <jwt_access_token>
```

**Response (204):** No content

**Validation Rules:**
- Cannot delete categories with existing transactions
- Cannot delete categories with subcategories
- Must delete/reassign subcategories first

**Error Response (400):**
```json
{
    "error": "Cannot delete category with existing transactions"
}
```

## Custom Actions

### GET /api/finance/categories/tree/
Get categories organized as a hierarchical tree structure.

**Response (200):**
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "category_type": "string",
            "color": "string",
            "icon": "string",
            "subcategories": [
                {
                    "id": "integer",
                    "name": "string",
                    "color": "string",
                    "icon": "string",
                    "transaction_count": "integer"
                }
            ]
        }
    ]
}
```

### GET /api/finance/categories/by_type/
Get categories grouped by type (income/expense).

**Response (200):**
```json
{
    "income": {
        "count": "integer",
        "categories": [
            {
                "id": "integer",
                "name": "string",
                "description": "string",
                "color": "string",
                "icon": "string",
                "subcategory_count": "integer",
                "transaction_count": "integer"
            }
        ]
    },
    "expense": {
        "count": "integer",
        "categories": [
            {
                "id": "integer",
                "name": "string",
                "description": "string",
                "color": "string",
                "icon": "string",
                "subcategory_count": "integer",
                "transaction_count": "integer"
            }
        ]
    }
}
```

## Category Types

### Income Categories
- `salary`: Salary/Wages
- `freelance`: Freelance Income
- `investment`: Investment Returns
- `business`: Business Income
- `other_income`: Other Income

### Expense Categories
- `housing`: Housing/Rent
- `food`: Food & Dining
- `transportation`: Transportation
- `utilities`: Utilities
- `entertainment`: Entertainment
- `healthcare`: Healthcare
- `shopping`: Shopping
- `other_expense`: Other Expenses

## Hierarchical Structure

### Parent-Child Relationships
- Categories can have subcategories (children)
- Subcategories inherit type from parent
- Maximum depth: 2 levels (parent -> child)
- Parent categories cannot be deleted if they have children

### Tree Structure Example
```
Expenses
├── Housing
│   ├── Rent
│   ├── Utilities
│   └── Maintenance
├── Food
│   ├── Groceries
│   ├── Restaurants
│   └── Takeout
└── Transportation
    ├── Gas
    ├── Public Transit
    └── Car Maintenance
```

## Security Features

### Data Isolation
- Users can only access their own categories
- All queries filtered by `owner=request.user`
- Category creation automatically assigns current user as owner

### Validation
- Category names must be unique per user per level
- Parent category must belong to same user
- Category type must match parent's type

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
- **Category has transactions**: "Cannot delete category with existing transactions"
- **Category has subcategories**: "Cannot delete category with subcategories"
- **Duplicate name**: "Category with this name already exists"
- **Invalid parent**: "Parent category must belong to you"
- **Type mismatch**: "Subcategory type must match parent type"

## Dependencies
- Django REST Framework
- Django Filters

## Related Models
- **Transaction**: Transactions reference categories
- **Budget**: Budgets can be filtered by categories

## Business Logic

### Category Creation
1. Validate category data using `CategorySerializer`
2. Check name uniqueness within user's categories
3. Validate parent category ownership and type
4. Set owner to current authenticated user
5. Create category record

### Category Deletion
1. Check for existing transactions using this category
2. Check for subcategories under this category
3. Prevent deletion if either condition exists
4. Require manual cleanup before deletion

### Tree Structure Building
1. Fetch parent categories (parent=null)
2. For each parent, fetch subcategories
3. Build hierarchical structure for frontend

## Integration Points
- **Transaction Service**: Categories used to classify transactions
- **Budget Service**: Categories used for budget filtering
- **Reporting**: Categories used for expense/income analysis
- **Frontend**: Tree structure for category selection

## Performance Considerations
- Indexed fields: `owner`, `category_type`, `parent`, `is_active`
- Efficient queries for tree structure building
- Cached transaction counts for categories

## Default Categories

### System-Provided Categories
On user registration, default categories can be created:

**Income Categories:**
- Salary
- Freelance
- Investments
- Other Income

**Expense Categories:**
- Housing
- Food & Dining
- Transportation
- Utilities
- Entertainment
- Healthcare
- Shopping
- Other Expenses

## Testing Considerations
- Test category creation with parent-child relationships
- Test category deletion validation
- Test tree structure generation
- Test category type grouping
- Test data isolation between users
- Test name uniqueness validation
- Test hierarchical validation rules
- Test transaction count accuracy