#!/bin/bash
set -e

echo "==============================================="
echo "RescueMesh Backend - Container Startup"
echo "==============================================="

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h db -p 5432 -U rescuemesh > /dev/null 2>&1; do
  sleep 1
done
echo "✅ PostgreSQL is ready"

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect static files (for production)
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Load initial data if database is empty (idempotent)
echo "🔍 Checking if database needs initialization..."
MISSION_COUNT=$(python manage.py shell -c "
from apps.missions.models import Mission
print(Mission.objects.count())
" 2>/dev/null || echo "0")

if [ "$MISSION_COUNT" = "0" ]; then
  echo "📥 Loading initial data..."
  
  # Seed use case templates (collapsed building, cave rescue, etc.)
  echo "  - Seeding use case templates..."
  python manage.py seed_usecases || echo "  ⚠️  Use case seeding skipped or failed"
  
  # Create demo missions with fixed UUIDs (required for frontend)
  echo "  - Creating demo missions..."
  python manage.py seed_demo_missions || echo "  ⚠️  Demo mission creation skipped or failed"
  
  # Load digital twin terrain data (if available)
  if [ -f /data/processed/migovec_sample.json ]; then
    echo "  - Loading digital twin sites..."
    python manage.py seed_digital_twins || echo "  ⚠️  Digital twin seeding skipped or failed"
  fi
  
  # Load mission scenarios (if available)
  if [ -d /data/scenarios ]; then
    echo "  - Loading mission scenarios..."
    python manage.py seed_mission_scenarios || echo "  ⚠️  Scenario seeding skipped or failed"
  fi
  
  echo "✅ Initial data loading completed"
else
  echo "✅ Database already populated ($MISSION_COUNT missions found)"
fi

# Create superuser if specified (for admin access)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "👤 Creating superuser..."
  python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created')
else:
    print('Superuser already exists')
" || echo "  ⚠️  Failed to create superuser"
fi

# Reset stale simulations (important for container restarts)
echo "🔄 Resetting all simulations to fresh state..."
python manage.py reset_stale_simulations --reset-all || echo "  ⚠️  Simulation reset skipped or failed"

echo "==============================================="
echo "🚀 Starting Django development server..."
echo "==============================================="

# Start Django server
exec python manage.py runserver 0.0.0.0:8000
