# Just Travel - Docker Deployment Guide

Complete guide for running Just Travel in Docker containers with full PWA support.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [Building & Running](#building--running)
5. [Architecture](#architecture)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)

---

## 🚀 Quick Start

```bash
# 1. Clone and navigate to project
cd just-travel-app

# 2. Copy environment variables
cp .env.example .env

# 3. Edit .env with your API keys
nano .env  # or vim, or any editor

# 4. Build and start all services
docker-compose up --build

# 5. Access the application
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# Redis:    localhost:6379
```

That's it! The app should be running with full PWA functionality.

---

## 📦 Prerequisites

### Required Software
- **Docker:** v20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose:** v2.0+ ([Install Compose](https://docs.docker.com/compose/install/))

### Verify Installation
```bash
docker --version        # Should show 20.10+
docker-compose --version  # Should show 2.0+
```

### Required API Keys
At minimum, you need:
- ✅ **GOOGLE_API_KEY** - For AI agents (Gemini)
- ✅ **GOOGLE_PLACES_API_KEY** - For location data

Optional (but recommended):
- ⬜ OPENWEATHER_API_KEY - Weather forecasts
- ⬜ AMADEUS_CLIENT_ID/SECRET - Flight intelligence
- ⬜ GOOGLE_CLIENT_ID/SECRET - OAuth login

---

## ⚙️ Configuration

### Step 1: Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit with your favorite editor
nano .env
```

### Step 2: Required Variables

**Minimum Configuration:**
```bash
# AI & Location Services (REQUIRED)
GOOGLE_API_KEY=AIza...your-key
GOOGLE_PLACES_API_KEY=AIza...your-key

# Security (CHANGE THESE!)
SECRET_KEY=generate-a-random-32-char-string
NEXTAUTH_SECRET=generate-another-random-string
```

**Generate Secure Secrets:**
```bash
# For SECRET_KEY and NEXTAUTH_SECRET
openssl rand -hex 32
```

### Step 3: Optional Services

**Weather Integration:**
```bash
OPENWEATHER_API_KEY=your-key-from-openweathermap.org
```

**Flight Intelligence:**
```bash
AMADEUS_CLIENT_ID=your-client-id
AMADEUS_CLIENT_SECRET=your-client-secret
```

**Google OAuth:**
```bash
GOOGLE_CLIENT_ID=your-oauth-client-id
GOOGLE_CLIENT_SECRET=your-oauth-client-secret
```

---

## 🏗️ Building & Running

### Development Mode

```bash
# Build images
docker-compose build

# Start services (detached)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Mode

```bash
# Build with production optimizations
docker-compose build --no-cache

# Start with resource limits
docker-compose up -d

# Check health status
docker-compose ps
```

### Individual Services

```bash
# Start only backend + redis
docker-compose up -d backend redis

# Start only frontend
docker-compose up -d frontend

# Restart a specific service
docker-compose restart backend
```

---

## 🏛️ Architecture

### Services Overview

```
┌─────────────────────────────────────────────────────┐
│                   User's Browser                     │
│              (PWA with Offline Support)              │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP
           ┌──────────┴──────────┐
           │                     │
   ┌───────▼────────┐   ┌───────▼────────┐
   │   Frontend     │   │    Backend     │
   │   (Next.js)    │◄──┤    (FastAPI)   │
   │   Port: 3000   │   │   Port: 8000   │
   └────────────────┘   └───────┬────────┘
           │                     │
           │            ┌────────▼────────┐
           │            │     Redis       │
           │            │  (Task Queue)   │
           │            │   Port: 6379    │
           │            └─────────────────┘
           │
   ┌───────▼────────┐
   │   IndexedDB    │
   │ (Offline Data) │
   └────────────────┘
```

### Container Details

#### 1. **Backend Container**
- **Image:** Python 3.12-slim
- **Port:** 8000
- **Purpose:**
  - FastAPI REST API
  - 6 AI agents (Profiler, Pathfinder, TrendSpotter, Concierge, Optimizer, CreativeDirector)
  - Background task coordination
- **Volumes:**
  - `./data` → SQLite database
  - `./uploads` → User uploads
- **Health Check:** `/api/health` endpoint

#### 2. **Frontend Container**
- **Image:** Node 20-alpine
- **Port:** 3000
- **Purpose:**
  - Next.js 14 app
  - PWA with service worker
  - IndexedDB for offline storage
- **Build:** Multi-stage (deps → builder → runner)
- **Health Check:** HTTP GET to root

#### 3. **Redis Container**
- **Image:** Redis 7-alpine
- **Port:** 6379
- **Purpose:**
  - PWA background task status
  - Async media generation tracking
- **Persistence:** Volume-mounted `/data`
- **Health Check:** `redis-cli ping`

### Network Communication

```bash
# Internal Docker Network: just-travel-network

Frontend → Backend: http://backend:8000
Backend → Redis:    redis://redis:6379/0

# External Access
Browser → Frontend: http://localhost:3000
Browser → Backend:  http://localhost:8000 (API calls)
```

---

## 📊 Monitoring & Management

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Check Service Health

```bash
# Status of all services
docker-compose ps

# Expected output:
# NAME                  STATUS              PORTS
# just-travel-backend   Up (healthy)        8000/tcp
# just-travel-frontend  Up (healthy)        3000/tcp
# just-travel-redis     Up (healthy)        6379/tcp
```

### Resource Usage

```bash
# Real-time stats
docker stats

# Service-specific
docker stats just-travel-backend
```

### Execute Commands in Containers

```bash
# Backend: Python shell
docker-compose exec backend python

# Backend: Database shell
docker-compose exec backend python -c "from database import *"

# Frontend: Node shell
docker-compose exec frontend node

# Redis: CLI
docker-compose exec redis redis-cli
```

---

## 🗄️ Data Persistence

### Volumes

```bash
# List volumes
docker volume ls | grep just-travel

# Inspect redis volume
docker volume inspect just-travel-redis-data

# Backup redis data
docker run --rm -v just-travel-redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz -C /data .

# Restore redis data
docker run --rm -v just-travel-redis-data:/data -v $(pwd):/backup alpine tar xzf /backup/redis-backup.tar.gz -C /data
```

### Database Backup

```bash
# Backup SQLite database
docker-compose exec backend cp /app/data/just_travel.db /app/data/just_travel.db.backup

# Or from host
cp ./data/just_travel.db ./data/just_travel.db.backup
```

---

## 🐛 Troubleshooting

### Issue: Containers Won't Start

**Check logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

**Common causes:**
- Missing `.env` file
- Invalid API keys
- Port conflicts (8000, 3000, 6379 already in use)

**Solution:**
```bash
# Check what's using ports
lsof -i :8000
lsof -i :3000
lsof -i :6379

# Stop conflicting services
docker-compose down

# Rebuild
docker-compose up --build
```

### Issue: Backend Health Check Failing

**Symptom:**
```
backend    | unhealthy
```

**Check:**
```bash
# View backend logs
docker-compose logs backend | tail -50

# Test health endpoint manually
curl http://localhost:8000/api/health
```

**Common causes:**
- Missing Python dependencies
- Database initialization failed
- API keys not set

**Solution:**
```bash
# Rebuild backend
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Issue: Frontend Not Connecting to Backend

**Symptom:** Network errors in browser console

**Check environment:**
```bash
docker-compose exec frontend env | grep API_URL
# Should show: NEXT_PUBLIC_API_URL=http://backend:8000
```

**Solution:**
```bash
# Ensure correct network settings in .env
echo "NEXT_PUBLIC_API_URL=http://backend:8000" >> .env

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Issue: Redis Connection Refused

**Check Redis status:**
```bash
docker-compose exec redis redis-cli ping
# Should return: PONG
```

**Check backend can reach Redis:**
```bash
docker-compose exec backend python -c "
import redis
r = redis.from_url('redis://redis:6379/0')
print(r.ping())
"
# Should print: True
```

### Issue: PWA Not Installing

**Checklist:**
1. ✓ Running HTTPS in production? (Required for PWA)
2. ✓ Service worker registered? (Check DevTools → Application)
3. ✓ Manifest accessible? (Visit http://localhost:3000/manifest.json)
4. ✓ Icons loading? (Check public/icons/)

**Test manifest:**
```bash
curl http://localhost:3000/manifest.json
```

### Issue: Build Takes Too Long

**Speed up builds:**
```bash
# Use BuildKit
DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose build

# Parallel builds
docker-compose build --parallel
```

---

## 🚀 Production Deployment

### Pre-Production Checklist

- [ ] **Security:**
  - [ ] Change `SECRET_KEY` and `NEXTAUTH_SECRET`
  - [ ] Use strong, unique secrets (32+ characters)
  - [ ] Set `NODE_ENV=production`
  - [ ] Enable HTTPS/SSL

- [ ] **Performance:**
  - [ ] Build with `--no-cache`
  - [ ] Set resource limits
  - [ ] Enable Redis persistence
  - [ ] Configure log rotation

- [ ] **Monitoring:**
  - [ ] Set up health check monitoring
  - [ ] Configure alerts
  - [ ] Enable log aggregation
  - [ ] Track resource usage

### Docker Compose Production Overrides

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    restart: always
    environment:
      - NODE_ENV=production
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

  frontend:
    restart: always
    environment:
      - NODE_ENV=production
      - NEXT_TELEMETRY_DISABLED=1
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 256M

  redis:
    restart: always
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

**Run in production:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### HTTPS/SSL Setup

**Option 1: Nginx Reverse Proxy**

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Option 2: Traefik (Automatic SSL)**

Add Traefik service to docker-compose:

```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - --providers.docker=true
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.myresolver.acme.email=your@email.com
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

### Backup Strategy

```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/just-travel"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
docker-compose exec -T backend cat /app/data/just_travel.db > "$BACKUP_DIR/db_$DATE.sqlite"

# Backup Redis
docker-compose exec -T redis redis-cli BGSAVE
docker cp just-travel-redis:/data/dump.rdb "$BACKUP_DIR/redis_$DATE.rdb"

# Rotate old backups (keep last 7 days)
find "$BACKUP_DIR" -name "*.sqlite" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.rdb" -mtime +7 -delete
```

### Monitoring

**Docker Health Checks:**
```bash
# Check all services
watch -n 5 'docker-compose ps'

# Alert on unhealthy
docker-compose ps | grep -q "unhealthy" && echo "ALERT: Service unhealthy!"
```

**Prometheus + Grafana:**
- Expose metrics from FastAPI
- Monitor container resources
- Track API response times
- Alert on errors

---

## 🔒 Security Best Practices

1. **Never commit .env to version control**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use Docker secrets in production**
   ```yaml
   services:
     backend:
       secrets:
         - google_api_key
   secrets:
     google_api_key:
       external: true
   ```

3. **Run as non-root user**
   - Frontend already uses non-root (nextjs:nodejs)
   - Backend should too (add to Dockerfile)

4. **Scan images for vulnerabilities**
   ```bash
   docker scan just-travel-backend
   docker scan just-travel-frontend
   ```

5. **Keep images updated**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

---

## 📚 Additional Resources

- **Docker Compose Docs:** https://docs.docker.com/compose/
- **Next.js Docker:** https://nextjs.org/docs/deployment#docker-image
- **FastAPI Docker:** https://fastapi.tiangolo.com/deployment/docker/
- **Redis Docker:** https://hub.docker.com/_/redis

---

## 🆘 Getting Help

**Check logs first:**
```bash
docker-compose logs -f
```

**Inspect containers:**
```bash
docker-compose ps
docker inspect just-travel-backend
```

**Test connectivity:**
```bash
# From host
curl http://localhost:8000/api/health
curl http://localhost:3000

# Between containers
docker-compose exec frontend wget -qO- http://backend:8000/api/health
```

---

**Docker Guide Version:** 1.0
**Last Updated:** February 6, 2026
**Full PWA Support:** ✅ Enabled
