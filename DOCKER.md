# Docker Deployment Guide

This guide explains how to run the Just Travel app using Docker and Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0+)

## Quick Start

### 1. Set Up Environment Variables

Copy the example environment file and fill in your API keys:

```bash
cp just-travel-app/.env.example just-travel-app/.env
```

Edit `just-travel-app/.env` and add at minimum your Google Gemini API key:

```env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

See [just-travel-app/API_KEYS.md](just-travel-app/API_KEYS.md) for details on all available API keys.

### 2. Build and Run

From the project root directory:

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Stop the Application

```bash
# Stop services (keep containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (⚠️ deletes database)
docker-compose down -v
```

## Architecture

The Docker setup consists of two services:

```
┌─────────────────────────────────────────┐
│  Frontend (Next.js 14)                  │
│  Container: just-travel-frontend        │
│  Port: 3000                             │
│  Image: Node 20 Alpine (multi-stage)    │
└─────────────────┬───────────────────────┘
                  │
                  │ HTTP
                  ▼
┌─────────────────────────────────────────┐
│  Backend (FastAPI)                      │
│  Container: just-travel-backend         │
│  Port: 8000                             │
│  Image: Python 3.12 Slim                │
│  Database: SQLite (volume mounted)      │
└─────────────────────────────────────────┘
```

### Service Details

**Backend (`just-travel-backend`)**:
- FastAPI app with 6 AI agents
- Python 3.12 runtime
- SQLite database persisted via volume mount
- Health checks enabled
- Automatic restart on failure

**Frontend (`just-travel-frontend`)**:
- Next.js 14 app with standalone output
- Node 20 Alpine runtime
- Multi-stage build for optimized image size
- Runs as non-root user for security
- Waits for backend health check before starting

## Development Workflow

### Rebuilding After Code Changes

```bash
# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Rebuild and restart
docker-compose up -d --build
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Running Commands Inside Containers

```bash
# Execute command in backend container
docker-compose exec backend python -c "print('Hello')"

# Execute command in frontend container
docker-compose exec frontend npm run lint

# Open shell in backend
docker-compose exec backend bash

# Open shell in frontend
docker-compose exec frontend sh
```

## Database Management

The SQLite database is persisted using volume mounts:

```bash
# Database location on host
./just-travel-app/just_travel.db

# Database location in container
/app/just_travel.db
```

### Backup Database

```bash
# Copy database from container
docker-compose exec backend cp /app/just_travel.db /app/data/backup.db

# Copy to host
docker cp just-travel-backend:/app/data/backup.db ./backup.db
```

### Reset Database

```bash
# Stop services
docker-compose down

# Remove database file
rm just-travel-app/just_travel.db

# Restart (will create fresh database)
docker-compose up -d
```

## Production Considerations

### Security

1. **Use secrets management**: Don't commit `.env` files with real API keys
2. **Enable HTTPS**: Use a reverse proxy (nginx/traefik) with SSL certificates
3. **Limit network exposure**: Only expose necessary ports
4. **Update base images**: Regularly rebuild with latest security patches

### Example with Nginx Reverse Proxy

```yaml
# Add to docker-compose.yml
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - frontend
      - backend
```

### Scaling

```bash
# Scale backend instances (requires load balancer)
docker-compose up -d --scale backend=3
```

## Troubleshooting

### Port Already in Use

If ports 3000 or 8000 are already in use, modify `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # Use different host port
```

### Container Won't Start

Check logs:

```bash
docker-compose logs backend
docker-compose logs frontend
```

### API Keys Not Working

Ensure `.env` file exists and has correct values:

```bash
# Verify environment variables in container
docker-compose exec backend printenv | grep GOOGLE_API_KEY
```

### Database Permission Issues

```bash
# Fix ownership
sudo chown -R $USER:$USER just-travel-app/just_travel.db
chmod 644 just-travel-app/just_travel.db
```

### Clean Slate

Remove everything and start fresh:

```bash
# Stop and remove containers, networks, and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Rebuild from scratch
docker-compose up --build
```

## Performance Optimization

### Multi-Stage Builds

Both Dockerfiles use multi-stage builds to minimize image size:

- **Backend**: ~200 MB (vs ~1 GB without optimization)
- **Frontend**: ~150 MB (vs ~800 MB without optimization)

### Build Cache

Docker caches layers. To maximize cache hits:

1. Dependencies are installed before copying source code
2. `.dockerignore` files exclude unnecessary files
3. Use `--no-cache` flag only when needed:

```bash
docker-compose build --no-cache
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build images
        run: docker-compose build

      - name: Run tests
        run: |
          docker-compose up -d
          docker-compose exec -T backend pytest
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Next.js Docker Guide](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)
