# RescueMesh Docker Deployment Guide

This guide will help you deploy the RescueMesh Mission Platform using Docker and Docker Compose.

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum (4GB recommended)
- 5GB disk space

### 1. Clone and Configure

```bash
# Navigate to project directory
cd rescue_mesh

# Create environment file from example
cp .env.example .env

# Edit .env with your configuration
# IMPORTANT: Change DB_PASSWORD and DJANGO_SECRET_KEY!
nano .env  # or your preferred editor
```

### 2. Start Services

```bash
# Build and start all containers
docker-compose up -d

# View logs
docker-compose logs -f

# Wait for initialization (first run takes 30-60 seconds)
```

### 3. Access the Application

- **Frontend**: http://localhost:4321
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

### 4. Verify Deployment

```bash
# Check container status
docker-compose ps

# Should show 3 healthy containers:
# - rescuemesh_db (PostgreSQL + PostGIS)
# - rescuemesh_backend (Django)
# - rescuemesh_frontend (Astro)

# Test API endpoint
curl http://localhost:8000/api/v1/missions/

# Test frontend
curl http://localhost:4321/
```

---

## 📋 Container Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Astro + Node.js)                             │
│  Container: rescuemesh_frontend                         │
│  Port: 4321                                             │
│  Purpose: Static site + interactive islands             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Backend (Django + DRF)                                 │
│  Container: rescuemesh_backend                          │
│  Port: 8000                                             │
│  Purpose: REST API + simulation engine                  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Database (PostgreSQL 15 + PostGIS)                     │
│  Container: rescuemesh_db                               │
│  Port: 5432                                             │
│  Volume: postgres_data (persistent)                     │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuration

### Environment Variables (.env)

**Required:**
- `DB_PASSWORD` - PostgreSQL password (use strong password!)
- `DJANGO_SECRET_KEY` - Django secret key (generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)

**Optional:**
- `DEBUG=False` - Set to False for production
- `ALLOWED_HOSTS=your-domain.com` - Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS=https://your-domain.com` - Frontend origin for CORS
- `FRONTEND_PORT=4321` - Change frontend port
- `BACKEND_PORT=8000` - Change backend port
- `DB_PORT=5432` - Change database port

### Creating Django Superuser

```bash
# Option 1: Set in .env before first start
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=secure_password
DJANGO_SUPERUSER_EMAIL=admin@rescuemesh.local

# Option 2: Create manually after startup
docker-compose exec backend python manage.py createsuperuser
```

---

## 🔧 Common Commands

### Container Management

```bash
# Start services
docker-compose up -d

# Stop services (preserves data)
docker-compose down

# Stop and remove volumes (deletes data!)
docker-compose down -v

# Restart specific service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build

# View logs
docker-compose logs -f
docker-compose logs backend  # Specific container
```

### Django Commands

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Django shell
docker-compose exec backend python manage.py shell

# Collect static files
docker-compose exec backend python manage.py collectstatic

# Load fixtures
docker-compose exec backend python manage.py seed_digital_twins
docker-compose exec backend python manage.py seed_mission_scenarios
```

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U rescuemesh -d rescuemesh

# Backup database
docker-compose exec db pg_dump -U rescuemesh rescuemesh > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U rescuemesh rescuemesh < backup.sql

# View database size
docker-compose exec db psql -U rescuemesh -d rescuemesh -c "SELECT pg_size_pretty(pg_database_size('rescuemesh'));"
```

### Monitoring

```bash
# View container resource usage
docker stats

# Check container health
docker-compose ps

# View Django cache statistics
docker-compose exec backend python manage.py shell
>>> from apps.missions.services.scenario_engine import load_scenario_cached
>>> print(load_scenario_cached.cache_info())
```

---

## 🔒 Production Deployment

### Security Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Generate strong `DJANGO_SECRET_KEY`
- [ ] Use strong `DB_PASSWORD` (32+ characters)
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Update `CORS_ALLOWED_ORIGINS` with your frontend URL
- [ ] Enable HTTPS (use reverse proxy like nginx)
- [ ] Set up automatic backups
- [ ] Configure log rotation
- [ ] Enable firewall rules
- [ ] Set up monitoring alerts

### Recommended VPS Providers

| Provider | Cost/Month | Specs | Best For |
|----------|-----------|-------|----------|
| **Hetzner Cloud** | €4.51 | 4GB RAM, 40GB SSD | Best value |
| **DigitalOcean** | $12 | 2GB RAM, 50GB SSD | Easy setup |
| **Linode** | $12 | 2GB RAM, 50GB SSD | Good docs |
| **AWS Lightsail** | $10 | 2GB RAM, 60GB SSD | AWS integration |

### Production docker-compose.yml

For production, create `docker-compose.prod.yml`:

```yaml
version: '3.9'

services:
  db:
    image: postgis/postgis:15-3.3
    restart: always
    environment:
      POSTGRES_DB: rescuemesh
      POSTGRES_USER: rescuemesh
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    secrets:
      - db_password
    networks:
      - internal

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
    environment:
      - DEBUG=False
      - DJANGO_SECRET_KEY_FILE=/run/secrets/django_secret
    secrets:
      - django_secret
    depends_on:
      - db
    networks:
      - internal

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - static_volume:/static:ro
    depends_on:
      - backend
      - frontend
    networks:
      - internal

secrets:
  db_password:
    file: ./secrets/db_password.txt
  django_secret:
    file: ./secrets/django_secret.txt

volumes:
  postgres_data:
  static_volume:

networks:
  internal:
    driver: bridge
```

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if database is ready
docker-compose exec db pg_isready -U rescuemesh

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Backend Won't Start

```bash
# Check backend logs
docker-compose logs backend

# Verify migrations
docker-compose exec backend python manage.py showmigrations

# Run migrations manually
docker-compose exec backend python manage.py migrate

# Check environment variables
docker-compose exec backend env | grep DJANGO
```

### Port Conflicts

If ports 4321, 8000, or 5432 are already in use:

```bash
# Edit .env file
FRONTEND_PORT=4322
BACKEND_PORT=8001
DB_PORT=5433

# Restart services
docker-compose down
docker-compose up -d
```

### Performance Issues

```bash
# Check container resource usage
docker stats

# Check Django query count
docker-compose logs backend | grep -i "query"

# Verify cache is working
docker-compose exec backend python manage.py shell
>>> from apps.missions.services.scenario_engine import load_scenario_cached
>>> print(load_scenario_cached.cache_info())
# Should show high hit ratio: CacheInfo(hits=147, misses=3, ...)
```

### Data Loss Prevention

```bash
# Regular backups (add to crontab)
0 2 * * * docker-compose exec db pg_dump -U rescuemesh rescuemesh | gzip > /backups/rescuemesh_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz

# Test restore periodically
docker-compose exec -T db psql -U rescuemesh rescuemesh < test_backup.sql
```

---

## 📊 Performance Expectations

With Docker + PostgreSQL + lru_cache:

- **Container startup**: 5-10 seconds
- **First API request**: ~50ms (3 DB queries)
- **Subsequent requests**: <1ms (cached)
- **Database load**: ~3 queries total per container restart
- **Memory usage**: ~500MB total (all containers)
- **Disk usage**: ~2GB (with data)
- **Concurrent users**: 50-100 without issues
- **Response time**: <100ms average

---

## 📚 Additional Resources

- **Full Docker Deployment Guide**: `.github/instructions/docker-deployment.instructions.md`
- **Backend API Docs**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin
- **PostgreSQL + PostGIS**: https://registry.hub.docker.com/r/postgis/postgis
- **Docker Compose Docs**: https://docs.docker.com/compose/

---

## 🆘 Getting Help

If you encounter issues:

1. Check container logs: `docker-compose logs -f`
2. Verify environment configuration: `.env` file
3. Review troubleshooting section above
4. Check Docker and database status
5. Consult full deployment instructions in `.github/instructions/`

---

## 🎉 Success!

If you see:
- ✅ 3 containers running (`docker-compose ps`)
- ✅ Frontend accessible at http://localhost:4321
- ✅ Backend API responding at http://localhost:8000/api/v1/missions/
- ✅ Mission simulations working in dashboard

**Your RescueMesh platform is successfully deployed!** 🚀
