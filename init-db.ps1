# RescueMesh Database Initialization Script (PowerShell)
# Run this inside the backend container to seed the database

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "RescueMesh Database Initialization" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Run migrations
Write-Host "📦 Running migrations..." -ForegroundColor Yellow
docker-compose exec backend python manage.py migrate

# Seed use case templates
Write-Host "📥 Seeding use case templates..." -ForegroundColor Yellow
docker-compose exec backend python manage.py seed_usecases

# Create demo missions
Write-Host "🎯 Creating demo missions..." -ForegroundColor Yellow
docker-compose exec backend python manage.py seed_demo_missions

# Optional: Seed digital twin data
Write-Host "🗺️  Seeding digital twin terrain data (optional)..." -ForegroundColor Yellow
docker-compose exec backend python manage.py seed_digital_twins

Write-Host ""
Write-Host "=======================================" -ForegroundColor Green
Write-Host "✅ Database initialization complete!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Testing database..." -ForegroundColor Yellow
docker-compose exec backend python manage.py shell -c "from apps.missions.models import Mission; print(f'Total missions: {Mission.objects.count()}')"
Write-Host ""
Write-Host "🎉 RescueMesh is ready! Access at http://localhost:4321" -ForegroundColor Green
