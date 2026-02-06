# Docker Quick Reference

## 🚀 Common Commands

### Start & Stop
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Build & Rebuild
```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build frontend

# Rebuild from scratch (no cache)
docker-compose build --no-cache

# Build and start
docker-compose up --build -d
```

### View Logs
```bash
# All services (follow mode)
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Since 5 minutes ago
docker-compose logs --since 5m
```

### Check Status
```bash
# Service status
docker-compose ps

# Resource usage
docker stats

# Health checks
docker-compose ps | grep healthy
```

### Execute Commands
```bash
# Python shell (backend)
docker-compose exec backend python

# Node shell (frontend)
docker-compose exec frontend node

# Redis CLI
docker-compose exec redis redis-cli

# Bash shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

---

## 🔧 Maintenance

### Clean Up
```bash
# Stop and remove containers
docker-compose down

# Remove volumes too
docker-compose down -v

# Remove everything (including images)
docker-compose down --rmi all -v

# Prune unused images
docker image prune -a

# Clean system
docker system prune -a
```

### Database
```bash
# Backup
docker-compose exec backend cp /app/data/just_travel.db /app/data/backup.db

# View database
docker-compose exec backend sqlite3 /app/data/just_travel.db

# Check tables
docker-compose exec backend sqlite3 /app/data/just_travel.db ".tables"
```

### Redis
```bash
# Check Redis data
docker-compose exec redis redis-cli KEYS '*'

# Get task status
docker-compose exec redis redis-cli GET "task:YOUR_TASK_ID"

# Flush all data (CAREFUL!)
docker-compose exec redis redis-cli FLUSHALL
```

---

## 📊 Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend health
curl http://localhost:3000

# Redis health
docker-compose exec redis redis-cli ping
```

### Resource Monitoring
```bash
# Live stats
docker stats --no-stream

# Memory usage
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"

# CPU usage
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}"
```

---

## 🐛 Debugging

### Service Not Starting
```bash
# Check logs
docker-compose logs backend

# Check if port is already in use
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :6379  # Redis

# Restart service
docker-compose restart backend
```

### Network Issues
```bash
# Test connectivity between services
docker-compose exec frontend wget -qO- http://backend:8000/api/health

# Check network
docker network ls | grep just-travel
docker network inspect just-travel-network
```

### Build Failures
```bash
# Build with verbose output
docker-compose build --progress=plain

# Build specific service
docker-compose build --no-cache backend

# Check Dockerfile syntax
docker build -f Dockerfile -t test .
```

---

## 📦 Data Management

### Volumes
```bash
# List volumes
docker volume ls | grep just-travel

# Inspect volume
docker volume inspect just-travel-redis-data

# Backup volume
docker run --rm -v just-travel-redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz -C /data .

# Restore volume
docker run --rm -v just-travel-redis-data:/data -v $(pwd):/backup alpine tar xzf /backup/redis-backup.tar.gz -C /data
```

### Database Files
```bash
# Location on host
ls -lah ./data/

# Backup
cp ./data/just_travel.db ./data/backup_$(date +%Y%m%d).db

# Restore
cp ./data/backup_20260206.db ./data/just_travel.db
```

---

## 🔒 Security

### Environment Variables
```bash
# View container env vars
docker-compose exec backend env

# Check sensitive vars are set
docker-compose exec backend env | grep -E "API_KEY|SECRET"
```

### Secrets Management
```bash
# Generate secure secrets
openssl rand -hex 32

# Check .env is not in image
docker-compose exec backend ls -la .env  # Should fail
```

---

## 🚀 Performance

### Optimize Build
```bash
# Use BuildKit
DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose build

# Parallel builds
docker-compose build --parallel
```

### Resource Limits
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

---

## 📍 Quick Troubleshooting Matrix

| Issue | Command | Expected Result |
|-------|---------|----------------|
| Service unhealthy | `docker-compose logs backend` | Check for errors |
| Port conflict | `lsof -i :8000` | See what's using port |
| Database locked | `docker-compose restart backend` | Restart service |
| Redis connection | `docker-compose exec redis redis-cli ping` | Should return PONG |
| Build failing | `docker-compose build --no-cache` | Fresh build |
| Network error | `docker network inspect just-travel-network` | Check connections |
| Out of disk | `docker system prune -a` | Clean up |

---

## 🎯 Common Workflows

### Fresh Install
```bash
cd just-travel-app
cp .env.example .env
nano .env  # Add API keys
docker-compose up --build -d
docker-compose logs -f
```

### Update Code
```bash
git pull
docker-compose build
docker-compose up -d
```

### Debug Backend
```bash
docker-compose logs -f backend
docker-compose exec backend python
docker-compose exec backend cat /app/data/just_travel.db
```

### Debug Frontend
```bash
docker-compose logs -f frontend
docker-compose exec frontend sh
docker-compose exec frontend ls -la public/
```

### Reset Everything
```bash
docker-compose down -v
rm -rf data/ uploads/
docker-compose up --build -d
```

---

## 📚 Help

- Full Guide: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- Docker Docs: https://docs.docker.com/
- Compose Docs: https://docs.docker.com/compose/
