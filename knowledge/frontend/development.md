# Frontend Development Guide

## Overview

The Prism frontend is built with **React 18**, **TypeScript**, **TailwindCSS**, **shadcn/ui**, and **Framer Motion**. It follows modern React patterns and provides a comprehensive financial management interface.

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS + shadcn/ui components
- **Animation**: Framer Motion
- **Routing**: React Router DOM
- **Forms**: React Hook Form + Zod validation
- **State Management**: React Context + Hooks
- **HTTP Client**: Axios with interceptors

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui base components
│   └── layout/         # Layout components (Sidebar, Header)
├── contexts/           # React contexts (Auth, etc.)
├── hooks/              # Custom React hooks
├── lib/                # Utilities and helpers
├── pages/              # Page components
│   └── auth/          # Authentication pages
├── services/           # API services and HTTP client
└── types/              # TypeScript type definitions
```

## Key Features

### Authentication System
- JWT-based authentication with automatic token refresh
- Protected routes with redirect handling
- Context-based state management
- Form validation with Zod schemas

### UI Components
- Custom shadcn/ui implementation
- Consistent design system with CSS variables
- Responsive design (mobile-first)
- Dark/light theme support (via CSS variables)

### Navigation & Layout
- Sidebar navigation with active state indicators
- Protected layout wrapper
- Animated page transitions with Framer Motion
- Search functionality in header

### Financial Management Pages
- **Dashboard**: Overview with stats and charts
- **Accounts**: Account management interface
- **Transactions**: Transaction listing and management
- **Budgets**: Budget tracking with progress bars
- **Goals**: Financial goal progress tracking

## Development Setup

### Prerequisites
- Node.js 20.19+ (current version warnings can be ignored for development)
- npm or yarn

### Installation
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
```

### Building for Production
```bash
npm run build
```

### Environment Variables
Create `.env` file:
```
VITE_API_URL=http://localhost:8000
```

## Component Guidelines

### UI Components
- Use shadcn/ui components as base
- Extend with TailwindCSS utilities
- Follow compound component patterns
- Include proper TypeScript interfaces

### Page Components
- Use motion components for page transitions
- Implement proper loading states
- Handle error boundaries
- Include proper SEO meta tags

### Form Components
- Use React Hook Form for form state
- Implement Zod validation schemas
- Provide accessible error messages
- Include loading states for submissions

## API Integration

### Service Layer
The `apiService` provides:
- Automatic JWT token handling
- Request/response interceptors
- Automatic token refresh
- Error handling

### Authentication Flow
1. Login/Register → Store tokens in localStorage
2. API requests automatically include Bearer token
3. 401 responses trigger token refresh
4. Failed refresh redirects to login

### Data Fetching Patterns
```typescript
// Service function
export const userService = {
  async getProfile() {
    return apiService.get<User>('/api/users/profile/')
  }
}

// Component usage
const { user, loading, error } = useAuth()
```

## Styling Guidelines

### TailwindCSS
- Use utility classes for rapid development
- Create component classes for repeated patterns
- Follow mobile-first responsive design
- Use semantic color names (primary, secondary, etc.)

### shadcn/ui Integration
- Customize via CSS variables in `index.css`
- Extend component variants as needed
- Maintain consistent spacing and typography
- Use provided icon system (Lucide React)

## Animation Guidelines

### Framer Motion
- Keep animations subtle (< 250ms)
- Use consistent easing functions
- Implement page transitions
- Add loading state animations
- Consider user preferences (reduced motion)

### Animation Types
- **Page transitions**: Fade + slide
- **Component entry**: Stagger animations
- **Hover states**: Scale + color changes
- **Loading states**: Spin or pulse animations

## Testing Strategy

### Unit Testing
- Test utility functions
- Test custom hooks
- Test component behavior
- Mock API calls

### Integration Testing
- Test authentication flows
- Test form submissions
- Test navigation
- Test API error handling

### E2E Testing
- Test complete user journeys
- Test responsive behavior
- Test accessibility
- Test performance

## Performance Optimization

### Code Splitting
- Lazy load pages with React.lazy()
- Split vendor bundles
- Optimize third-party imports

### Asset Optimization
- Optimize images and icons
- Use WebP format where possible
- Implement proper caching headers
- Minimize bundle size

### Runtime Performance
- Memoize expensive calculations
- Optimize re-renders with React.memo
- Use proper dependency arrays
- Implement virtual scrolling for large lists

## Accessibility

### WCAG Compliance
- Proper semantic HTML
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance
- Focus management

### Implementation
- Use shadcn/ui accessible components
- Add proper ARIA labels
- Implement skip links
- Test with screen readers

## Security Considerations

### Authentication
- Store tokens securely
- Implement proper logout
- Handle token expiration
- Validate user permissions

### Data Handling
- Sanitize user inputs
- Validate on both client and server
- Implement CSRF protection
- Use HTTPS in production

## Deployment

### Build Process
1. Run type checking: `npm run tsc`
2. Build assets: `npm run build`
3. Test build: `npm run preview`

### Environment Configuration
- Production API URLs
- Analytics configuration
- Error tracking setup
- Performance monitoring

## Troubleshooting

### Common Issues
1. **Node version warnings**: Can be ignored for development
2. **TailwindCSS not loading**: Check PostCSS configuration
3. **API calls failing**: Verify CORS settings and API URLs
4. **Authentication issues**: Check token storage and refresh logic

### Debug Tools
- React Developer Tools
- TailwindCSS Inspector
- Network tab for API calls
- Console for error logging