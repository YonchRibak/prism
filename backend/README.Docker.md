# Docker Setup for Prism Backend

This document explains how to run the Prism backend using Docker.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Clone the repository and navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Copy environment variables:**
   ```bash
   cp .env.example .env
   ```

3. **Edit the .env file with your configuration:**
   ```bash
   # Update SECRET_KEY, DATABASE_URL, etc.
   ```

4. **Build and start the services:**
   ```bash
   docker-compose up --build
   ```

The application will be available at:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs/
- PostgreSQL: localhost:5432

## Development Setup

For development with hot reloading:

```bash
# Start with development override
docker-compose up --build

# The override file automatically enables development mode
```

## Production Setup

For production deployment:

```bash
# Start with production services (including nginx)
docker-compose --profile production up --build -d
```

## Available Services

- **web**: Django application server
- **db**: PostgreSQL database
- **nginx**: Reverse proxy (production only)

## Environment Variables

Key environment variables in `.env`:

```env
DEBUG=0  # Set to 0 for production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://prism_user:prism_password@db:5432/prism_db
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Common Commands

### Database Management

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access Django shell
docker-compose exec web python manage.py shell

# Access database
docker-compose exec db psql -U prism_user -d prism_db
```

### Container Management

```bash
# View logs
docker-compose logs web
docker-compose logs db

# Restart services
docker-compose restart web

# Stop all services
docker-compose down

# Remove volumes (⚠️ This will delete your database)
docker-compose down -v
```

### Building and Testing

```bash
# Rebuild containers
docker-compose build

# Run tests
docker-compose exec web python manage.py test

# Check container status
docker-compose ps
```

## Ports

- **8000**: Django development server
- **80**: Nginx (production)
- **5432**: PostgreSQL database

## Volumes

- `postgres_data`: PostgreSQL data persistence
- `static_volume`: Static files for nginx

## Health Checks

Both the web and database services include health checks:
- Database: `pg_isready`
- Web: HTTP request to `/api/docs/`

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change ports in docker-compose.yml or stop conflicting services
   ```

2. **Database connection issues:**
   ```bash
   # Check database is running
   docker-compose ps db

   # Check database logs
   docker-compose logs db
   ```

3. **Permission issues:**
   ```bash
   # Reset file permissions
   chmod -R 755 .
   ```

4. **Build failures:**
   ```bash
   # Clean build
   docker-compose build --no-cache
   ```

### Accessing Container Shell

```bash
# Web container
docker-compose exec web bash

# Database container
docker-compose exec db bash
```

## Security Notes

- Change default passwords in production
- Use environment variables for sensitive data
- Configure proper firewall rules
- Use HTTPS in production
- Regular security updates

## Performance Tips

- Use volume mounts for development only
- In production, copy code into container
- Configure appropriate worker counts for gunicorn
- Monitor resource usage

## Backup and Restore

### Database Backup
```bash
docker-compose exec db pg_dump -U prism_user prism_db > backup.sql
```

### Database Restore
```bash
docker-compose exec -T db psql -U prism_user prism_db < backup.sql
```