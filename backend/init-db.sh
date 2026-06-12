#!/bin/bash
# RescueMesh Database Reseed Script
# Run inside the backend container.

set -e

echo "======================================="
echo "RescueMesh Database Reseed"
echo "======================================="
echo ""

echo "Running migrations..."
python manage.py migrate

echo "Re-seeding use case templates..."
python manage.py seed_usecases --clear

echo "Creating or updating fixed demo missions..."
python manage.py seed_demo_missions

if [ -d /data/processed ]; then
  echo "Re-seeding digital twin terrain data..."
  python manage.py seed_digital_twins --clear
else
  echo "Skipping digital twin terrain data: /data/processed not mounted"
fi

echo "Re-seeding mission scenarios..."
python manage.py seed_mission_scenarios --all --overwrite

echo "Re-seeding media artifacts..."
python manage.py seed_media_artifacts --clear

echo "Resetting simulations..."
python manage.py reset_stale_simulations --reset-all

if [ -n "$1" ] && [ "$1" = "--superuser" ]; then
  echo ""
  echo "Creating Django superuser..."
  python manage.py createsuperuser
fi

echo ""
echo "======================================="
echo "Database reseed complete"
echo "======================================="
echo ""
echo "Available missions:"
python manage.py shell -c "
from apps.missions.models import Mission
for m in Mission.objects.all():
    print(f'  - {m.name} (ID: {m.id})')
"
echo ""
