# RescueMesh Database Reseed Script (PowerShell)
# Run from the repository root while the Docker containers are running.

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "RescueMesh Database Reseed" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Running migrations..." -ForegroundColor Yellow
docker-compose exec backend python manage.py migrate

Write-Host "Re-seeding use case templates..." -ForegroundColor Yellow
docker-compose exec backend python manage.py seed_usecases --clear

Write-Host "Creating or updating fixed demo missions..." -ForegroundColor Yellow
docker-compose exec backend python manage.py seed_demo_missions

Write-Host "Re-seeding digital twin terrain data..." -ForegroundColor Yellow
docker-compose exec backend python manage.py seed_digital_twins --clear

Write-Host "Re-seeding mission scenarios..." -ForegroundColor Yellow
docker-compose exec backend python manage.py seed_mission_scenarios --all --overwrite

Write-Host "Re-seeding media artifacts..." -ForegroundColor Yellow
docker-compose exec backend python manage.py seed_media_artifacts --clear

Write-Host "Resetting simulations..." -ForegroundColor Yellow
docker-compose exec backend python manage.py reset_stale_simulations --reset-all

Write-Host ""
Write-Host "=======================================" -ForegroundColor Green
Write-Host "Database reseed complete" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""

Write-Host "Testing database..." -ForegroundColor Yellow
docker-compose exec backend python manage.py shell -c "from apps.missions.models import Mission; from apps.usecases.models import UseCaseTemplate; print(f'Total use cases: {UseCaseTemplate.objects.count()}'); print(f'Total missions: {Mission.objects.count()}')"

Write-Host ""
Write-Host "RescueMesh is ready at http://localhost:4321" -ForegroundColor Green
