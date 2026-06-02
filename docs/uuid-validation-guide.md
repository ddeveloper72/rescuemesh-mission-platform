# UUID Validation and Management Guide

## Overview

RescueMesh uses UUIDs to identify missions. When the database is recreated (e.g., Docker volume removal, seeding, or database reset), new UUIDs are generated. This can cause **UUID mismatch errors** where the frontend has stale UUIDs that don't exist in the current database.

This guide explains the UUID validation system and how to prevent/fix UUID mismatch issues.

---

## UUID Validation Layers

We implement validation at **three layers** to catch issues early:

### 1. **Backend Validation** (Django)

**Location:** `backend/apps/missions/validators.py`

**Features:**
- UUID format validation
- Mission existence checks
- Detailed error messages with suggestions
- Health check endpoint

**Health Check Endpoint:**
```bash
GET http://localhost:8000/api/v1/missions/health/
```

**Response:**
```json
{
  "status": "healthy",
  "missions_count": 5,
  "missions": [
    {
      "uuid": "c5d0ffd4-2fc8-4b45-841d-88ec93f27e8e",
      "name": "Collapsed Building Search Demo",
      "scenario": "collapsed-building-search",
      "use_case": "collapsed-building-search",
      "status": "ready"
    }
  ],
  "timestamp": "2026-06-01T20:45:00Z",
  "warning": "If you see different UUIDs than expected, rebuild frontend..."
}
```

**Enhanced Error Messages:**

When a mission UUID is not found, the API returns:
```
Mission not found: 2c6ccd68-85f6-49ac-b28d-6f5358bc6a68

Possible causes:
  1. Database was recreated (run: docker compose build --no-cache frontend)
  2. Mission was deleted
  3. Wrong environment (dev vs production)

Available missions:
  - c5d0ffd4-2fc8-4b45-841d-88ec93f27e8e (Collapsed Building Search Demo - collapsed-building-search)
  - 063218cf-7662-4675-8337-edabd204b793 (Cave Rescue Demo - cave-rescue)

To get current mission UUIDs: GET /api/v1/missions/health/
```

---

### 2. **Frontend Runtime Validation** (TypeScript)

**Location:** `frontend/src/lib/uuid-validation.ts`

**Features:**
- UUID format validation before API calls
- UUID mismatch detection (valid format but 404 response)
- Graceful error handling with user-friendly messages
- Development mode warnings for hardcoded UUIDs

**Usage in Simulation Manager:**
```typescript
import { validateMissionUUID, isUUIDMismatchError } from './uuid-validation';

// Validate before initializing
const result = validateMissionUUID(missionPk);
if (!result.valid) {
  throw new Error(`UUID validation failed: ${result.error}`);
}

// Check if 404 error is due to UUID mismatch
if (isUUIDMismatchError(error, missionPk)) {
  console.error(getUUIDMismatchGuidance(missionPk));
}
```

**User-Facing Error:**

When a UUID mismatch is detected, the dashboard shows:

```
⚠️ Mission Not Found (UUID Mismatch)

The mission UUID c5d0ffd4-... doesn't exist in the current database.

This usually means the database was recreated but the frontend has stale UUIDs.

To fix:
1. Rebuild frontend: docker compose build --no-cache frontend
2. Restart frontend: docker compose up -d frontend
3. Or view available missions: Health Check
```

---

### 3. **Build-Time Validation** (Astro SSR)

**Location:** `frontend/src/lib/build-uuid-validator.ts`

**Features:**
- Validates mission UUIDs during static site generation
- Fetches current UUIDs from backend `/health/` endpoint
- Prevents deploying pages with stale UUIDs
- Fails build if missions not found (strict mode)

**Usage in Astro Pages:**
```typescript
---
import { requireMissionForBuild } from '../../../lib/build-uuid-validator';

// Strict: Fails build if mission not found
const missionData = await requireMissionForBuild('collapsed-building-search');
const MISSION_PK = missionData.missionPk;
---

<div data-mission-pk={MISSION_PK}>
  <!-- ... -->
</div>
```

**Build Output:**
```
[Build Validator] ✅ Found mission for collapsed-building-search: c5d0ffd4-...
[Build Validator] ✅ Found mission for cave-rescue: 063218cf-...
[Build Validator] ✅ Found mission for flooded-structure: 2c6ccd68-...
```

**Build Failure Example:**
```
❌ Build-time validation failed!

No mission found for scenario: collapsed-building-search

  - Run backend seeding: docker exec rescuemesh_backend python manage.py seed_scenarios
  - Check available scenarios in backend
  - Available missions: cave-rescue, flooded-structure
```

---

## Common Scenarios and Solutions

### Scenario 1: Database Recreated (Docker Volume Removed)

**Symptom:** Frontend shows 404 errors, simulation won't start

**Cause:** New UUIDs generated during database seeding, frontend has old UUIDs

**Solution:**
```bash
# Rebuild frontend to fetch fresh UUIDs
docker compose build --no-cache frontend
docker compose up -d frontend

# Or full reset
docker compose down
docker compose up -d
```

---

### Scenario 2: Development After Backend Seeding

**Symptom:** Astro build fails with "Mission not found"

**Cause:** Backend was reseeded, UUIDs changed

**Solution:**
```bash
# Check current missions
curl http://localhost:8000/api/v1/missions/health/ | jq

# Rebuild frontend
cd frontend
npm run build

# Or in Docker
docker compose build frontend
```

---

### Scenario 3: Stale Browser Cache

**Symptom:** Old UUIDs persist even after rebuilding

**Cause:** Browser cached old static files

**Solution:**
```bash
# Hard refresh in browser
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)

# Or clear browser cache for localhost
```

---

### Scenario 4: Docker Cache Issues

**Symptom:** Build completes but still has old UUIDs

**Cause:** Docker layer caching preserved old dist/ folder

**Solution:**
```bash
# Complete Docker reset
docker compose down
docker system prune -af --volumes
docker compose build --no-cache
docker compose up -d

# Wait for seeding to complete (check logs)
docker compose logs -f backend
```

---

## Best Practices

### 1. **Always Use Health Check After Database Changes**

```bash
# After seeding
curl http://localhost:8000/api/v1/missions/health/

# Save UUIDs for reference
curl http://localhost:8000/api/v1/missions/health/ | jq '.missions[] | {scenario, uuid}' > mission-uuids.json
```

### 2. **Use Build-Time Validation in Astro Pages**

```typescript
---
// ❌ Bad: Hardcoded UUID
const MISSION_PK = 'c5d0ffd4-2fc8-4b45-841d-88ec93f27e8e';

// ✅ Good: Fetch from API at build time
import { requireMissionForBuild } from '../../../lib/build-uuid-validator';
const missionData = await requireMissionForBuild('collapsed-building-search');
const MISSION_PK = missionData.missionPk;
---
```

### 3. **Add Error Containers to Astro Pages**

```astro
<!-- Add before main content -->
<div id="mission-error-banner" class="hidden"></div>

<!-- Error will be shown here if UUID validation fails -->
```

### 4. **Monitor Build Logs**

```bash
# Watch for validation messages during build
docker compose build frontend 2>&1 | grep "Build Validator"
```

### 5. **Use No-Cache Rebuild After Database Recreation**

```bash
# Database was recreated
docker compose exec backend python manage.py seed_scenarios

# ALWAYS rebuild frontend with --no-cache
docker compose build --no-cache frontend
docker compose up -d frontend
```

---

## Development Workflow

### Daily Development

```bash
# 1. Start services
docker compose up -d

# 2. Verify missions
curl http://localhost:8000/api/v1/missions/health/

# 3. Develop frontend
cd frontend
npm run dev

# 4. Frontend automatically fetches current UUIDs during dev build
```

### After Database Changes

```bash
# 1. Recreate database or reseed
docker compose down -v
docker compose up -d

# 2. Wait for seeding
docker compose logs -f backend | grep "seed"

# 3. Rebuild frontend
docker compose build --no-cache frontend
docker compose up -d frontend

# 4. Verify UUIDs match
curl http://localhost:8000/api/v1/missions/health/
```

### Production Deployment

```bash
# 1. Ensure backend is seeded
docker compose exec backend python manage.py check_missions

# 2. Build frontend (validates at build time)
docker compose build frontend

# 3. Deploy
docker compose up -d

# 4. Health check
curl http://localhost:8000/api/v1/missions/health/
```

---

## Debugging Commands

### Check Current Mission UUIDs
```bash
# Via API
curl http://localhost:8000/api/v1/missions/health/ | jq

# Via Django shell
docker compose exec backend python manage.py shell
>>> from apps.missions.models import Mission
>>> Mission.objects.values('pk', 'name', 'scenario__slug')
```

### Check Built Frontend UUIDs
```bash
# Extract UUIDs from built HTML
docker exec rescuemesh_frontend grep -r 'data-mission-pk=' /app/dist/demo/live/ | grep -o 'data-mission-pk="[^"]*"'

# Compare with backend
diff <(docker exec rescuemesh_backend python -c "from apps.missions.models import Mission; print('\\n'.join(str(m.pk) for m in Mission.objects.all()))") \
     <(docker exec rescuemesh_frontend grep -rh 'data-mission-pk=' /app/dist/demo/live/ | grep -o '[0-9a-f-]\{36\}' | sort | uniq)
```

### Force Clean Rebuild
```bash
# Nuclear option: complete reset
docker compose down -v
docker system prune -af --volumes
rm -rf frontend/node_modules frontend/dist
docker compose build --no-cache
docker compose up -d
```

---

## Error Reference

### `Invalid UUID format: "..."`
**Cause:** UUID string doesn't match expected format
**Fix:** Check data-mission-pk attribute, ensure it's a valid UUID v4

### `Mission not found: [uuid]`
**Cause:** Valid UUID but doesn't exist in database
**Fix:** Rebuild frontend with `--no-cache`

### `Health check failed: 404`
**Cause:** Backend not running or health endpoint not configured
**Fix:** Start backend, check Django URLs configuration

### `Build-time validation failed`
**Cause:** Backend unreachable during Astro build
**Fix:** Ensure backend is running before building frontend

---

## Architecture Notes

### Why Three Layers?

1. **Backend:** Catch issues at the source, provide detailed diagnostics
2. **Frontend Runtime:** Graceful degradation, user-friendly error messages
3. **Build-Time:** Prevent deploying broken builds, fail fast during CI/CD

### Why Not Use Slugs Instead of UUIDs?

- UUIDs are globally unique (multi-tenancy safe)
- UUIDs prevent ID collisions (dev vs prod)
- Django REST Framework defaults to UUIDs for security
- Slugs can be added as alternate lookup (future enhancement)

### Why Not Store UUIDs in Git?

- UUIDs change with every database recreation
- Storing them causes merge conflicts
- Dynamic fetching is more resilient

---

## Future Enhancements

1. **UUID Sync Script:**
   ```bash
   # Automatically sync UUIDs after database changes
   ./scripts/sync-mission-uuids.sh
   ```

2. **CI/CD Integration:**
   ```yaml
   # .github/workflows/frontend-build.yml
   - name: Validate Missions
     run: |
       docker compose up -d backend
       curl --retry 5 --retry-delay 2 http://localhost:8000/api/v1/missions/health/
       docker compose build frontend
   ```

3. **Slug-Based Lookup:**
   ```
   GET /api/v1/missions/by-scenario/collapsed-building-search/
   ```

4. **Mission Metadata in Health Check:**
   ```json
   {
     "last_seeded": "2026-06-01T20:00:00Z",
     "database_id": "rescue_mesh_v1",
     "seed_version": "1.0.0"
   }
   ```

---

## Summary

**Always remember:**

1. ✅ Use health check endpoint after database changes
2. ✅ Rebuild frontend with `--no-cache` after seeding
3. ✅ Use build-time validation in Astro pages
4. ✅ Monitor build logs for validation warnings
5. ✅ Add error containers to handle UUID mismatches gracefully

**When in doubt:**
```bash
docker compose down
docker compose up -d backend
# Wait for seeding
docker compose build --no-cache frontend
docker compose up -d frontend
curl http://localhost:8000/api/v1/missions/health/
```
