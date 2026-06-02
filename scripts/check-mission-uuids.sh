#!/bin/bash
#
# Mission UUID Health Check Script
#
# Quick utility to check mission UUIDs and detect mismatches between
# database and frontend builds.
#
# Usage:
#   ./scripts/check-mission-uuids.sh

set -e

echo "🔍 RescueMesh Mission UUID Health Check"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if backend is running
echo "1️⃣  Checking backend status..."
if docker ps | grep -q rescuemesh_backend; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is not running${NC}"
    echo "   Start it with: docker compose up -d backend"
    exit 1
fi

echo ""

# Check if frontend is running
echo "2️⃣  Checking frontend status..."
if docker ps | grep -q rescuemesh_frontend; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend is not running${NC}"
fi

echo ""

# Fetch health check data
echo "3️⃣  Fetching mission UUIDs from backend..."
HEALTH_CHECK=$(curl -s http://localhost:8000/api/v1/missions/health/ || echo '{"status":"error"}')

if echo "$HEALTH_CHECK" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend health check OK${NC}"
    
    MISSION_COUNT=$(echo "$HEALTH_CHECK" | jq -r '.missions_count')
    echo "   Found $MISSION_COUNT missions"
    echo ""
    
    echo "4️⃣  Current Mission UUIDs:"
    echo "$HEALTH_CHECK" | jq -r '.missions[] | "   📍 \(.scenario): \(.uuid)"'
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo "   URL: http://localhost:8000/api/v1/missions/health/"
    echo "   Response: $HEALTH_CHECK"
    exit 1
fi

echo ""

# Check frontend UUIDs if container is running
if docker ps | grep -q rescuemesh_frontend; then
    echo "5️⃣  Checking frontend built UUIDs..."
    
    FRONTEND_UUIDS=$(docker exec rescuemesh_frontend sh -c "grep -rh 'data-mission-pk=' /app/dist/demo/live/ 2>/dev/null | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | sort | uniq" || echo "")
    
    if [ -z "$FRONTEND_UUIDS" ]; then
        echo -e "${YELLOW}⚠️  Could not extract UUIDs from frontend${NC}"
        echo "   Frontend may not be built yet"
    else
        echo "   Frontend has these UUIDs:"
        echo "$FRONTEND_UUIDS" | while read -r uuid; do
            # Check if this UUID exists in backend
            if echo "$HEALTH_CHECK" | jq -e --arg uuid "$uuid" '.missions[] | select(.uuid == $uuid)' > /dev/null 2>&1; then
                echo -e "   ${GREEN}✅ $uuid${NC}"
            else
                echo -e "   ${RED}❌ $uuid (NOT IN DATABASE!)${NC}"
            fi
        done
        
        # Check for any mismatches
        BACKEND_UUIDS=$(echo "$HEALTH_CHECK" | jq -r '.missions[].uuid' | sort)
        
        if [ "$BACKEND_UUIDS" = "$(echo "$FRONTEND_UUIDS")" ]; then
            echo ""
            echo -e "${GREEN}✅ All UUIDs match! Frontend and database are in sync.${NC}"
        else
            echo ""
            echo -e "${RED}⚠️  UUID MISMATCH DETECTED!${NC}"
            echo ""
            echo "Frontend has stale UUIDs that don't exist in the database."
            echo ""
            echo "To fix:"
            echo "   docker compose build --no-cache frontend"
            echo "   docker compose up -d frontend"
        fi
    fi
fi

echo ""
echo "========================================"
echo "Health check complete!"
echo ""
echo "📋 Available commands:"
echo "   View missions:  curl http://localhost:8000/api/v1/missions/health/ | jq"
echo "   Rebuild frontend:  docker compose build --no-cache frontend"
echo "   Restart services:  docker compose restart"
echo ""
