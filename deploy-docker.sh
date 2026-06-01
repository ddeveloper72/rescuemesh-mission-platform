#!/bin/bash
# RescueMesh Docker Quick Start Script
# Linux/macOS

set -e

echo "======================================="
echo "RescueMesh Docker Deployment"
echo "======================================="
echo ""

# Check if Docker is installed
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Install from: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✓ Docker found: $(docker --version)"

# Check if Docker Compose is available
echo "Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed"
    exit 1
fi
echo "✓ Docker Compose found: $(docker-compose --version)"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✓ Created .env file"
        echo ""
        echo "IMPORTANT: Edit .env and update these values:"
        echo "  - DB_PASSWORD (use a strong password!)"
        echo "  - DJANGO_SECRET_KEY (generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
        echo ""
        
        read -p "Open .env file now for editing? (Y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            ${EDITOR:-nano} .env
            echo ""
            read -p "Press Enter when you've finished editing .env"
        fi
    else
        echo "ERROR: .env.example not found"
        exit 1
    fi
else
    echo "✓ .env file exists"
fi
echo ""

# Build and start services
echo "Building and starting Docker containers..."
echo "This may take 2-5 minutes on first run..."
docker-compose up -d --build

echo ""
echo "✓ Containers started successfully!"
echo ""

# Wait for services to be ready
echo "Waiting for services to initialize (30 seconds)..."
sleep 30

# Check container status
echo ""
echo "Container Status:"
docker-compose ps

echo ""
echo "======================================="
echo "RescueMesh is Ready!"
echo "======================================="
echo ""
echo "Access your application:"
echo "  Frontend:     http://localhost:4321"
echo "  Backend API:  http://localhost:8000"
echo "  Django Admin: http://localhost:8000/admin"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart services: docker-compose restart"
echo "  Create superuser: docker-compose exec backend python manage.py createsuperuser"
echo ""
echo "Full documentation: DOCKER_DEPLOYMENT.md"
echo ""

# Offer to open browser (Linux with xdg-open, macOS with open)
read -p "Open frontend in browser? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:4321
    elif command -v open &> /dev/null; then
        open http://localhost:4321
    fi
fi
