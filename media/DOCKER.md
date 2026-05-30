# Docker Configuration for Generated Media

## Volume Configuration

The generated media system requires a writable directory for caching generated files.

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    volumes:
      # Mount generated media directory as writable volume
      - ./media/generated:/app/media/generated
      # Or use a named volume for persistence
      - generated_media:/app/media/generated
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings
    ports:
      - "8000:8000"
  
  frontend:
    build: ./frontend
    ports:
      - "4321:4321"
    depends_on:
      - backend

volumes:
  # Named volume for generated media (persists between container restarts)
  generated_media:
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create media directory with correct permissions
RUN mkdir -p /app/media/generated/images && \
    mkdir -p /app/media/generated/audio && \
    mkdir -p /app/media/generated/spectrograms && \
    chmod -R 777 /app/media/generated

# Expose media volume
VOLUME /app/media/generated

# Run Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Permissions

### Linux/Mac

```bash
# Ensure directory is writable
chmod -R 777 media/generated/

# Or set specific user ownership
chown -R 1000:1000 media/generated/
```

### Windows

```powershell
# Verify directory exists
if (!(Test-Path media\generated)) {
    New-Item -ItemType Directory -Path media\generated\images, media\generated\audio, media\generated\spectrograms
}
```

## Clear Cache in Docker

### Clear without restarting

```bash
# Access running container
docker exec -it rescuemesh-backend-1 sh

# Clear generated media
rm -rf /app/media/generated/images/*
rm -rf /app/media/generated/audio/*
rm -rf /app/media/generated/spectrograms/*

# Exit
exit
```

### Clear and reset volume

```bash
# Stop containers
docker-compose down

# Remove volume
docker volume rm rescuemesh_generated_media

# Restart (volume will be recreated)
docker-compose up -d
```

## Environment Variables

Optional configuration via environment variables:

```env
# Media generation settings (future)
GENERATED_MEDIA_CACHE_ENABLED=true
GENERATED_MEDIA_MAX_CACHE_SIZE_MB=1000
GENERATED_MEDIA_BASE_DIR=/app/media/generated
```

## Monitoring Cache Size

```bash
# Check cache size
docker exec rescuemesh-backend-1 du -sh /app/media/generated

# List generated files
docker exec rescuemesh-backend-1 find /app/media/generated -type f -name "*.png" -o -name "*.wav" | wc -l

# Show newest files
docker exec rescuemesh-backend-1 find /app/media/generated -type f -printf '%T+ %p\n' | sort -r | head -10
```

## Production Considerations

### Switching to S3

When transitioning to production with real mission media:

1. Add S3 configuration to Django settings
2. Update media storage backend to use S3
3. API endpoints remain the same
4. Frontend code unchanged
5. Generated media used as fallback

```python
# config/settings.py
if USE_S3_STORAGE:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
else:
    # Use local generated media
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media', 'generated')
```

### CDN Caching

For production, consider:
- CloudFront in front of S3
- Cache-Control headers
- Signed URLs for sensitive media
- Regional edge locations

## Troubleshooting

**"Permission denied" errors:**
```bash
# Fix permissions in container
docker exec -it rescuemesh-backend-1 chmod -R 777 /app/media/generated
```

**Volume not mounting:**
```bash
# Verify volume exists
docker volume ls | grep generated

# Inspect volume
docker volume inspect rescuemesh_generated_media

# Recreate volume
docker-compose down -v
docker-compose up -d
```

**Files not persisting between restarts:**
- Use named volume instead of bind mount
- Check volume configuration in docker-compose.yml
- Verify VOLUME directive in Dockerfile

**Cache growing too large:**
```bash
# Set up periodic cleanup (cron job)
0 2 * * * docker exec rescuemesh-backend-1 find /app/media/generated -type f -mtime +7 -delete
```

## Health Check

```bash
# Test media generation endpoint
curl http://localhost:8000/api/v1/missions/demo-test/generated-media/

# Test image generation
curl -o test.png http://localhost:8000/api/v1/generated-media/demo-test-image-001/preview/

# Test audio generation
curl -o test.wav http://localhost:8000/api/v1/generated-media/demo-test-audio-001/audio/

# Verify files were created
docker exec rescuemesh-backend-1 ls -lh /app/media/generated/images/
docker exec rescuemesh-backend-1 ls -lh /app/media/generated/audio/
```

## Performance Tuning

### Pregenerate Common Media

```python
# management/commands/pregenerate_media.py
from django.core.management.base import BaseCommand
from apps.media_generation.generators import image_generator, audio_generator

class Command(BaseCommand):
    help = 'Pregenerate common mission media for faster first load'
    
    def handle(self, *args, **options):
        # Generate common images
        for media_type in ['low_light', 'thermal', 'underwater']:
            image_generator.generate_and_save_image(
                f'common-{media_type}-001',
                media_type,
                'Demo Sector'
            )
        
        # Generate common audio
        for audio_type in ['knocking', 'tapping', 'voice_like']:
            audio_generator.generate_and_save_audio(
                f'common-{audio_type}-001',
                audio_type
            )
        
        self.stdout.write(self.style.SUCCESS('Pregeneration complete'))
```

Run in container:
```bash
docker exec rescuemesh-backend-1 python manage.py pregenerate_media
```

## Backup Strategy

```bash
# Backup generated media
docker exec rescuemesh-backend-1 tar -czf /tmp/media-backup.tar.gz /app/media/generated

# Copy from container
docker cp rescuemesh-backend-1:/tmp/media-backup.tar.gz ./backups/

# Restore
docker cp ./backups/media-backup.tar.gz rescuemesh-backend-1:/tmp/
docker exec rescuemesh-backend-1 tar -xzf /tmp/media-backup.tar.gz -C /
```

---

Generated media keeps RescueMesh portable, Docker-friendly, and cost-effective during development while maintaining production-ready architecture.
