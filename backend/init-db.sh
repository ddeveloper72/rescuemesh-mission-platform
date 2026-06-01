#!/bin/bash
# RescueMesh Database Initialization Script
# Run this inside the backend container to seed the database

set -e

echo "======================================="
echo "RescueMesh Database Initialization"
echo "======================================="
echo ""

# Run migrations
echo "📦 Running migrations..."
python manage.py migrate

# Seed use case templates
echo "📥 Seeding use case templates..."
python manage.py seed_usecases

# Create demo missions
echo "🎯 Creating demo missions..."
python manage.py seed_demo_missions

# Optional: Seed digital twin data
if [ -d /data/processed ]; then
  echo "🗺️  Seeding digital twin terrain data..."
  python manage.py seed_digital_twins || echo "⚠️  Digital twin seeding skipped"
fi

# Optional: Create superuser
if [ -n "$1" ] && [ "$1" = "--superuser" ]; then
  echo ""
  echo "👤 Creating Django superuser..."
  python manage.py createsuperuser
fi

echo ""
echo "======================================="
echo "✅ Database initialization complete!"
echo "======================================="
echo ""
echo "Available missions:"
python manage.py shell -c "
from apps.missions.models import Mission
for m in Mission.objects.all():
    print(f'  - {m.name} (ID: {m.id})')
"
echo ""
