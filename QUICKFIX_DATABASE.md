# 🚨 Quick Fix: Live Missions Not Starting

## Problem
Astro frontend loads, but live mission pages show "Loading..." or fail to start.

## Root Cause
Database is empty - no demo missions or use case templates were seeded.

---

## Solution (3 Steps)

### Option A: Rebuild Containers (Automatic - Recommended)

```powershell
# 1. Stop containers
docker-compose down

# 2. Rebuild backend with updated entrypoint script
docker-compose up -d --build backend

# 3. Watch initialization logs
docker-compose logs -f backend

# Wait for: "✅ Initial data loading completed"
# Then access: http://localhost:4321/demo/live/collapsed-building-search
```

### Option B: Manual Database Seeding (Quick Fix)

If containers are already running:

```powershell
# Run the initialization script
.\init-db.ps1

# Or manually run commands:
docker-compose exec backend python manage.py seed_usecases
docker-compose exec backend python manage.py seed_demo_missions
```

---

## Verification

Check that missions were created:

```powershell
# Should show 5 demo missions
docker-compose exec backend python manage.py shell -c "from apps.missions.models import Mission; print(f'Missions: {Mission.objects.count()}')"
```

Expected output: `Missions: 5`

Test API endpoint:

```powershell
# Should return mission data (not 404)
curl http://localhost:8000/api/v1/missions/c5d0ffd4-2fc8-4b45-841d-88ec93f27e8e/
```

---

## What Was Fixed

1. **Added missing `__init__.py` files** in `backend/apps/missions/management/` directory (required by Django)

2. **Updated `docker-entrypoint.sh`** to automatically run:
   - `python manage.py seed_usecases` - Creates use case templates
   - `python manage.py seed_demo_missions` - Creates 5 demo missions with fixed UUIDs

3. **Created helper scripts**:
   - `init-db.ps1` (Windows)
   - `backend/init-db.sh` (Linux/container)

---

## Testing Live Missions

After seeding, visit:

- http://localhost:4321/demo/live/collapsed-building-search
- http://localhost:4321/demo/live/cave-rescue
- http://localhost:4321/demo/live/flooded-structure
- http://localhost:4321/demo/live/industrial-inspection
- http://localhost:4321/demo/live/archaeological-exploration

Click **Start Mission** - simulation should begin with live updates.

---

## Optional: Create Admin User

```powershell
docker-compose exec backend python manage.py createsuperuser

# Then access: http://localhost:8000/admin
```

---

## Files Changed

✅ `backend/docker-entrypoint.sh` - Auto-seeds database on first run  
✅ `backend/apps/missions/management/__init__.py` - Django requirement  
✅ `backend/apps/missions/management/commands/__init__.py` - Django requirement  
✅ `init-db.ps1` - Manual database seeding helper  
✅ `backend/init-db.sh` - Container-internal seeding script  

---

## Next Steps

After confirming missions work:

1. ✅ Test simulation controls (Start/Pause/Reset/Speed)
2. ✅ Verify map updates in real-time
3. ✅ Check mission events in timeline panel
4. ✅ Test sensor detection markers

Your RescueMesh platform should now be fully functional! 🚀
