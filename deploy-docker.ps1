# RescueMesh Docker Quick Start Script
# Windows PowerShell

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "RescueMesh Docker Deployment" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>$null
if (-not $dockerVersion) {
    Write-Host "ERROR: Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green

# Check if Docker Compose is available
Write-Host "Checking Docker Compose..." -ForegroundColor Yellow
$composeVersion = docker-compose --version 2>$null
if (-not $composeVersion) {
    Write-Host "ERROR: Docker Compose is not installed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker Compose found: $composeVersion" -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env file" -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANT: Edit .env and update these values:" -ForegroundColor Red
        Write-Host "  - DB_PASSWORD (use a strong password!)" -ForegroundColor Yellow
        Write-Host "  - DJANGO_SECRET_KEY (generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" -ForegroundColor Yellow
        Write-Host ""
        
        $continue = Read-Host "Open .env file now for editing? (Y/n)"
        if ($continue -ne "n" -and $continue -ne "N") {
            notepad .env
            Write-Host ""
            Read-Host "Press Enter when you've finished editing .env"
        }
    } else {
        Write-Host "ERROR: .env.example not found" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ .env file exists" -ForegroundColor Green
}
Write-Host ""

# Build and start services
Write-Host "Building and starting Docker containers..." -ForegroundColor Yellow
Write-Host "This may take 2-5 minutes on first run..." -ForegroundColor Cyan
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to start Docker containers" -ForegroundColor Red
    Write-Host "Check logs with: docker-compose logs" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✓ Containers started successfully!" -ForegroundColor Green
Write-Host ""

# Wait for services to be ready
Write-Host "Waiting for services to initialize (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check container status
Write-Host ""
Write-Host "Container Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "=======================================" -ForegroundColor Green
Write-Host "RescueMesh is Ready!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access your application:" -ForegroundColor Cyan
Write-Host "  Frontend:     http://localhost:4321" -ForegroundColor White
Write-Host "  Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "  Django Admin: http://localhost:8000/admin" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  View logs:        docker-compose logs -f" -ForegroundColor White
Write-Host "  Stop services:    docker-compose down" -ForegroundColor White
Write-Host "  Restart services: docker-compose restart" -ForegroundColor White
Write-Host "  Create superuser: docker-compose exec backend python manage.py createsuperuser" -ForegroundColor White
Write-Host ""
Write-Host "Full documentation: DOCKER_DEPLOYMENT.md" -ForegroundColor Yellow
Write-Host ""

# Offer to open browser
$openBrowser = Read-Host "Open frontend in browser? (Y/n)"
if ($openBrowser -ne "n" -and $openBrowser -ne "N") {
    Start-Process "http://localhost:4321"
}
