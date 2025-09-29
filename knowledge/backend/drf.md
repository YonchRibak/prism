# Django REST Framework (DRF)

This app’s backend uses **Django + DRF** to expose a secure REST API.

---

## Structure
- `core/` → settings, auth, users.  
- `finance/` → models, serializers, views, filters, services.  
- `services/` handle business logic (analytics, CSV import, rules).  

---

## API
- **Base path**: `/api/v1/`  
- **Resources**: accounts, categories, transactions, budgets, goals, rules.  
- **Analytics**: summary, cashflow, category breakdown, budgets.  
- **Extras**: bulk transaction import, rule application.  
- Schema: generated with **drf-spectacular**.  

---

## Conventions
- All data scoped to `owner=request.user`.  
- Dates: accept `DD/MM/YYYY`, respond ISO (`YYYY-MM-DD`).  
- Expenses = negative, incomes = positive.  
- Pagination, filtering, ordering via DRF + django-filter.  

---

## Security
- Auth: JWT or token.  
- Enforce ownership at queryset level.  
- Rate limit writes.  
- Validate all uploads (CSV).  

---

## Deployment
- Postgres in production.  
- OpenAPI schema drives **swagger-typescript-codegen** for frontend client.  

---

# Summary
DRF provides a **schema-driven, per-user isolated API** with CRUD + analytics endpoints.  
Keep endpoints clean, enforce ownership, and let the schema guide the frontend client.
