# Mission UUID Health Check Script (PowerShell)
#
# Quick utility to check mission UUIDs and detect mismatches between
# database and frontend builds.
#
# Usage:
#   .\scripts\check-mission-uuids.ps1

Write-Host "🔍 RescueMesh Mission UUID Health Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
Write-Host "1️⃣  Checking backend status..." -ForegroundColor White
$backendRunning = docker ps | Select-String "rescuemesh_backend"
if ($backendRunning) {
    Write-Host "✅ Backend is running" -ForegroundColor Green
} else {
    Write-Host "❌ Backend is not running" -ForegroundColor Red
    Write-Host "   Start it with: docker compose up -d backend" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if frontend is running
Write-Host "2️⃣  Checking frontend status..." -ForegroundColor White
$frontendRunning = docker ps | Select-String "rescuemesh_frontend"
if ($frontendRunning) {
    Write-Host "✅ Frontend is running" -ForegroundColor Green
} else {
    Write-Host "⚠️  Frontend is not running" -ForegroundColor Yellow
}

Write-Host ""

# Fetch health check data
Write-Host "3️⃣  Fetching mission UUIDs from backend..." -ForegroundColor White
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/missions/health/" -Method Get
    
    if ($healthCheck.status -eq "healthy") {
        Write-Host "✅ Backend health check OK" -ForegroundColor Green
        Write-Host "   Found $($healthCheck.missions_count) missions"
        Write-Host ""
        
        Write-Host "4️⃣  Current Mission UUIDs:" -ForegroundColor White
        foreach ($mission in $healthCheck.missions) {
            Write-Host "   📍 $($mission.scenario): $($mission.uuid)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "❌ Backend health check failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Failed to fetch health check" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check frontend UUIDs if container is running
if ($frontendRunning) {
    Write-Host "5️⃣  Checking frontend built UUIDs..." -ForegroundColor White
    
    try {
        $frontendUuidsRaw = docker exec rescuemesh_frontend sh -c "grep -rh 'data-mission-pk=' /app/dist/demo/live/ 2>/dev/null | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | sort | uniq" 2>$null
        
        if ($frontendUuidsRaw) {
            $frontendUuids = $frontendUuidsRaw -split "`n" | Where-Object { $_ -match '\S' }
            
            Write-Host "   Frontend has these UUIDs:"
            
            $backendUuids = $healthCheck.missions | ForEach-Object { $_.uuid }
            $allMatch = $true
            
            foreach ($uuid in $frontendUuids) {
                $uuid = $uuid.Trim()
                if ($backendUuids -contains $uuid) {
                    Write-Host "   ✅ $uuid" -ForegroundColor Green
                } else {
                    Write-Host "   ❌ $uuid (NOT IN DATABASE!)" -ForegroundColor Red
                    $allMatch = $false
                }
            }
            
            # Check for any missing UUIDs
            foreach ($uuid in $backendUuids) {
                if ($frontendUuids -notcontains $uuid) {
                    Write-Host "   ⚠️  Missing from frontend: $uuid" -ForegroundColor Yellow
                    $allMatch = $false
                }
            }
            
            Write-Host ""
            if ($allMatch -and ($frontendUuids.Count -eq $backendUuids.Count)) {
                Write-Host "✅ All UUIDs match! Frontend and database are in sync." -ForegroundColor Green
            } else {
                Write-Host "⚠️  UUID MISMATCH DETECTED!" -ForegroundColor Red
                Write-Host ""
                Write-Host "Frontend has stale UUIDs that don't exist in the database." -ForegroundColor Yellow
                Write-Host ""
                Write-Host "To fix:"
                Write-Host "   docker compose build --no-cache frontend"
                Write-Host "   docker compose up -d frontend"
            }
        } else {
            Write-Host "⚠️  Could not extract UUIDs from frontend" -ForegroundColor Yellow
            Write-Host "   Frontend may not be built yet"
        }
    } catch {
        Write-Host "⚠️  Error checking frontend UUIDs: $_" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Health check complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Available commands:"
Write-Host "   View missions:  Invoke-RestMethod http://localhost:8000/api/v1/missions/health/ | ConvertTo-Json"
Write-Host "   Rebuild frontend:  docker compose build --no-cache frontend"
Write-Host "   Restart services:  docker compose restart"
Write-Host ""
