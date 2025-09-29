# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a financial management application with a Django REST Framework backend and React frontend. The project uses a knowledge-driven architecture with documentation in the `knowledge/` directory.

## Architecture

**Backend (Django + DRF):**
- `core/` - settings, authentication, user management
- `finance/` - models, serializers, views, filters, business logic services
- `services/` - analytics, CSV import, financial rules engine
- API base path: `/api/v1/`
- Authentication: JWT or token-based
- All data scoped per user (`owner=request.user`)
- OpenAPI schema generation with drf-spectacular

**Frontend (React):**
- TailwindCSS for utility-first styling
- shadcn/ui for accessible UI components
- Framer Motion for animations and transitions
- Design tokens defined in `tailwind.config.js`
- Generated TypeScript client from OpenAPI schema

## Data Conventions

- **Dates**: Accept `DD/MM/YYYY` format, respond with ISO format (`YYYY-MM-DD`)
- **Transactions**: Expenses are negative values, income is positive
- **Security**: All endpoints enforce user ownership at queryset level
- **Pagination**: Uses DRF + django-filter for filtering and ordering

## Development Guidelines

**Backend:**
- Enforce ownership isolation for all user data
- Rate limit write operations
- Validate all file uploads (CSV)
- Use services layer for complex business logic

**Frontend:**
- Mobile-first responsive design
- Keep animations under 250ms
- Use shadcn/ui as the foundation UI kit
- Follow Tailwind utility-first approach
- Animations should support UX flow, not distract

## Key Resources

- Backend API documentation: Generated OpenAPI schema
- Frontend components: Button, Input, Modal, Drawer, Table, Card, Progress
- Charts: Donut, Line, Bar with load animations
- Database: PostgreSQL in production

## Knowledge Base

Refer to the `knowledge/` directory for detailed documentation:
- `knowledge/backend/drf.md` - Django REST Framework specifics
- `knowledge/frontend/style.md` - Frontend styling guidelines
- `knowledge/admin/django_admin.md` - Admin interface
- `knowledge/architecture.md` - Overall architecture decisions