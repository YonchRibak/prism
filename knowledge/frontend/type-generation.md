# TypeScript Type Generation from Backend

## Overview

The Prism frontend automatically generates TypeScript types from the Django backend's OpenAPI schema, ensuring type safety and consistency between frontend and backend.

## Setup

### Dependencies
- `openapi-typescript`: Generates TypeScript types from OpenAPI 3.0 schemas
- `swagger-typescript-codegen`: Alternative generator (supports Swagger 2.0 only)
- `@openapitools/openapi-generator-cli`: Comprehensive generator (requires Java)

### Generated Files
```
src/types/
├── api-schema.ts       # Raw generated types from OpenAPI schema
└── api-types.ts        # Helper types and exports
```

## Usage

### Manual Type Generation
```bash
# Generate types from backend
npm run generate-types

# Alternative generators (if needed)
npm run generate-types-swagger   # Swagger 2.0 only
npm run generate-types-openapi   # Requires Java
```

### Automatic Generation During Development
```bash
# Start dev server with automatic type regeneration
npm run dev:types
```

This will:
1. Wait for backend to be available
2. Generate initial types
3. Watch for schema changes every 10 seconds
4. Regenerate types when backend schema updates
5. Start Vite development server

### Type Exports

```typescript
// Import specific types
import type { User, Account, Transaction } from '@/types/api-types'

// Import helper types
import type { PaginatedResponse, ApiError } from '@/types/api-types'

// Import all types
import type * as API from '@/types/api-types'
```

## Generated Type Structure

### Model Types
```typescript
export type User = {
  id: number
  email: string
  firstName: string
  lastName: string
  // ... other fields
}

export type Account = {
  id: number
  name: string
  accountType: 'checking' | 'savings' | 'credit'
  balance: number
  // ... other fields
}
```

### API Endpoint Types
```typescript
// Path types for all endpoints
export type ApiPaths = paths

// Response type extraction
export type AccountListResponse = ApiResponse<'/api/v1/accounts/', 'get'>

// Request body type extraction
export type CreateAccountRequest = ApiRequestBody<'/api/v1/accounts/', 'post'>
```

### Helper Types
```typescript
// Paginated responses
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// Error responses
export interface ApiError {
  detail?: string
  [key: string]: any
}
```

## Service Integration

### Typed API Services
All services use generated types for type safety:

```typescript
// services/accountService.ts
import type { Account, PaginatedResponse } from '@/types/api-types'

export const accountService = {
  async getAccounts(): Promise<PaginatedResponse<Account>> {
    return apiService.get<PaginatedResponse<Account>>('/api/v1/accounts/')
  },

  async createAccount(data: Omit<Account, 'id' | 'user' | 'balance'>): Promise<Account> {
    return apiService.post<Account>('/api/v1/accounts/', data)
  }
}
```

### React Integration
```typescript
// Using typed hooks
import { useAccounts } from '@/hooks/useApi'

function AccountsList() {
  const { data: accounts, loading, error } = useAccounts()

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div>
      {accounts?.results.map(account => (
        <div key={account.id}>{account.name}</div>
      ))}
    </div>
  )
}
```

## Type Generation Scripts

### Primary Script: `generate-types-simple.cjs`
Uses `openapi-typescript` for clean, modern type generation:
- ✅ Supports OpenAPI 3.0
- ✅ No external dependencies (Java)
- ✅ Fast generation
- ✅ Clean output

### Alternative Scripts

#### `generate-types-swagger.cjs`
Uses `swagger-typescript-codegen`:
- ❌ Swagger 2.0 only
- ✅ Includes API client generation
- ⚠️ Limited OpenAPI 3.0 support

#### `generate-types.cjs`
Uses `@openapitools/openapi-generator-cli`:
- ✅ Full OpenAPI 3.0 support
- ✅ Many output formats
- ❌ Requires Java
- ⚠️ Complex setup

## Configuration

### Environment Variables
```bash
VITE_API_URL=http://localhost:8000  # Backend URL for schema fetching
```

### Backend Requirements
The backend must expose an OpenAPI schema at `/api/schema/`:
- Django REST Framework with `drf-spectacular`
- CORS configured for development
- Schema endpoint accessible

## Workflow Integration

### Development Workflow
1. Start backend: `cd backend && python manage.py runserver`
2. Start frontend with types: `cd frontend && npm run dev:types`
3. Types automatically regenerate when backend schema changes

### Build Workflow
```bash
# Ensure types are up to date before building
npm run generate-types
npm run build
```

### CI/CD Integration
```yaml
# Example GitHub Actions step
- name: Generate API Types
  run: |
    # Wait for backend to be ready
    npm run generate-types

- name: Build Frontend
  run: npm run build
```

## Benefits

### Type Safety
- Compile-time validation of API calls
- Auto-completion in IDEs
- Catch API mismatches early

### Developer Experience
- IntelliSense for all API endpoints
- Automatic type inference
- Reduced manual type maintenance

### Consistency
- Single source of truth for API types
- Automatic synchronization with backend
- Eliminates type drift

## Troubleshooting

### Common Issues

#### Backend Not Available
```
❌ Failed to download schema. Make sure the backend is running.
```
**Solution**: Ensure Django backend is running on the configured URL.

#### Schema Format Issues
```
❌ Error: Only Swagger 2 specs are supported
```
**Solution**: Use `generate-types-simple.cjs` for OpenAPI 3.0 schemas.

#### Permission Issues
```
❌ EACCES: permission denied
```
**Solution**: Check file permissions in the `src/types/` directory.

#### CORS Issues
```
❌ Access to fetch at 'http://localhost:8000/api/schema/' blocked by CORS
```
**Solution**: Configure Django CORS settings for development.

### Debug Commands
```bash
# Check backend schema availability
curl http://localhost:8000/api/schema/

# Verify generated types
cat src/types/api-schema.ts | head -20

# Check type compilation
npx tsc --noEmit
```

## Best Practices

### Regular Updates
- Regenerate types after backend changes
- Include type generation in development workflow
- Version control generated types for team consistency

### Type Usage
- Always use generated types for API calls
- Extend types when needed rather than duplicating
- Use helper types for common patterns

### Error Handling
- Handle type generation failures gracefully
- Provide fallback types for development
- Log type generation issues in CI/CD

## Future Enhancements

### Planned Improvements
- Real-time type generation via WebSocket
- Integration with API documentation
- Custom type transformations
- Multiple backend support

### Advanced Features
- Type validation at runtime
- API mock generation from types
- Automated API testing from types
- Schema evolution tracking