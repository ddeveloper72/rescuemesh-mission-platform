# Error Handling & Resilience Guide

## Overview

RescueMesh implements comprehensive error handling for both frontend routing and backend API errors. This document describes the error resilience features and how to extend them.

---

## Frontend 404 Error Page

### Location
`frontend/src/pages/404.astro`

### Features
- **Automatic Handling**: Astro automatically serves this page for any unmatched routes
- **Mission-Themed Design**: Uses rescue/navigation metaphors consistent with platform branding
- **Helpful Navigation**: Provides 4 quick navigation cards to key sections
- **Clear Explanations**: Lists common reasons why users might see a 404
- **Consistent Styling**: Uses BaseLayout for header/footer consistency

### Triggers 404 Page
- Non-existent routes: `/this-does-not-exist`
- Typos in URLs: `/demo/colapsed-building` (missing 'l')
- Removed/renamed pages
- Bookmarks to old content
- External links pointing to moved resources

### Testing
```bash
# Test 404 page
curl http://localhost:4321/test-404
curl http://localhost:4321/invalid/route/here

# Should return page with title "404: Route Not Found | RescueMesh"
```

---

## API Error Handling

### Backend Response Patterns

#### 1. **404 Not Found**
When a resource doesn't exist (mission, scenario, media artifact):

```json
{
  "error": "Mission not found",
  "mission_id": "invalid-uuid-here"
}
```

**HTTP Status**: 404

#### 2. **400 Bad Request**
When request parameters are invalid:

```json
{
  "error": "Invalid parameter",
  "details": {
    "max_time": "Must be a positive number"
  }
}
```

**HTTP Status**: 400

#### 3. **500 Internal Server Error**
When unexpected errors occur:

```json
{
  "error": "Internal server error",
  "message": "Failed to calculate simulation state"
}
```

**HTTP Status**: 500

### API Endpoint Error Examples

#### Mission Not Found
```bash
GET /api/v1/missions/00000000-0000-0000-0000-000000000000/

Response: 404
{
  "detail": "Not found."
}
```

#### Media Artifacts - No Data
```bash
GET /api/v1/missions/{uuid}/media/?max_time=10

Response: 200
{
  "media_artifacts": [],
  "count": 0
}
```

#### Simulation State - Mission Exists But No Simulation
```bash
GET /api/v1/missions/{uuid}/simulation-state/

Response: 404
{
  "error": "No simulation exists for this mission"
}
```

---

## Frontend API Error Handling

### Current Pattern (lib/api.ts)

```typescript
export async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<APIResult<T>> {
  try {
    const response = await fetch(endpoint, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      return {
        success: false,
        error: `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}
```

### Recommended Frontend Error Handling

#### 1. **Display User-Friendly Messages**
```typescript
if (!result.success) {
  if (result.error?.includes('404')) {
    showNotification('Mission not found. It may have been deleted.');
  } else if (result.error?.includes('500')) {
    showNotification('Server error. Please try again later.');
  } else {
    showNotification('Network error. Check your connection.');
  }
}
```

#### 2. **Graceful Degradation**
```typescript
// If media fails to load, show placeholder
const mediaResult = await fetchAPI(API_ENDPOINTS.missions.media(missionId));
const media = mediaResult.success ? mediaResult.data : { media_artifacts: [], count: 0 };
```

#### 3. **Retry Logic for Transient Errors**
```typescript
async function fetchWithRetry<T>(
  endpoint: string,
  retries: number = 3
): Promise<APIResult<T>> {
  for (let i = 0; i < retries; i++) {
    const result = await fetchAPI<T>(endpoint);
    if (result.success || i === retries - 1) {
      return result;
    }
    await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
  }
  return { success: false, error: 'Max retries exceeded' };
}
```

---

## Backend Error Handling Best Practices

### 1. **Use DRF Exception Handlers**

Location: `backend/config/settings.py`

```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}
```

### 2. **Custom Exception Handler**

Location: `backend/apps/core/exceptions.py` (create if needed)

```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Call DRF's default handler first
    response = exception_handler(exc, context)
    
    # Log the error
    logger.error(f"API Error: {exc}", extra={'context': context})
    
    # Customize response format
    if response is not None:
        response.data = {
            'error': str(exc),
            'status_code': response.status_code,
            'path': context['request'].path,
        }
    
    return response
```

### 3. **Validation Errors**

```python
from rest_framework.serializers import ValidationError

def get_media_artifacts(self, request, pk=None):
    max_time = request.query_params.get('max_time')
    
    if max_time is not None:
        try:
            max_time = float(max_time)
            if max_time < 0:
                raise ValidationError({'max_time': 'Must be positive'})
        except ValueError:
            raise ValidationError({'max_time': 'Must be a number'})
```

---

## Docker Container Error Handling

### Health Checks

Location: `docker-compose.yml`

```yaml
services:
  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
  
  backend:
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Entrypoint Error Handling

Location: `backend/docker-entrypoint.sh`

```bash
set -e  # Exit on error

echo "🔍 Checking database connection..."
python manage.py wait_for_db || {
    echo "❌ Database connection failed"
    exit 1
}

echo "🔄 Running migrations..."
python manage.py migrate || {
    echo "❌ Migration failed"
    exit 1
}
```

---

## Testing Error Scenarios

### Frontend Tests

```typescript
describe('404 Error Page', () => {
  it('should display 404 page for invalid routes', async () => {
    const response = await fetch('http://localhost:4321/invalid-route');
    expect(response.status).toBe(404);
    const html = await response.text();
    expect(html).toContain('Route Not Found');
  });
});
```

### Backend API Tests

```python
def test_mission_not_found(self):
    """Test 404 response for non-existent mission."""
    response = self.client.get(
        '/api/v1/missions/00000000-0000-0000-0000-000000000000/'
    )
    self.assertEqual(response.status_code, 404)
    self.assertIn('error', response.json())

def test_invalid_media_time_parameter(self):
    """Test 400 response for invalid time parameter."""
    response = self.client.get(
        f'/api/v1/missions/{self.mission.id}/media/?max_time=invalid'
    )
    self.assertEqual(response.status_code, 400)
```

---

## Future Enhancements

### 1. **Error Tracking Service**
Integrate Sentry or similar service for production error monitoring:

```python
# backend/config/settings.py
if not DEBUG:
    import sentry_sdk
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        environment='production',
    )
```

### 2. **Rate Limiting**
Protect API from abuse:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

### 3. **Circuit Breaker Pattern**
Prevent cascading failures:

```typescript
class CircuitBreaker {
  private failures = 0;
  private threshold = 5;
  private timeout = 60000; // 1 minute
  private lastFailure = 0;
  
  async call<T>(fn: () => Promise<T>): Promise<T> {
    if (this.isOpen()) {
      throw new Error('Circuit breaker is open');
    }
    
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
  
  private isOpen(): boolean {
    return this.failures >= this.threshold &&
           Date.now() - this.lastFailure < this.timeout;
  }
}
```

### 4. **Offline Support**
Service Worker for PWA capabilities:

```javascript
// frontend/public/sw.js
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
      .catch(() => caches.match('/offline.html'))
  );
});
```

---

## Monitoring & Observability

### Key Metrics to Track

1. **Error Rate**: % of requests resulting in 4xx/5xx
2. **Response Time**: p50, p95, p99 latencies
3. **Availability**: Uptime percentage
4. **Error Types**: Distribution of error codes

### Logging Best Practices

```python
import logging
logger = logging.getLogger(__name__)

def simulation_state(self, request, pk=None):
    logger.info(f"Simulation state requested for mission {pk}")
    try:
        # ... logic ...
        logger.debug(f"Returned {len(agents)} agents")
    except Exception as e:
        logger.error(f"Simulation state failed: {e}", exc_info=True)
        raise
```

---

## Summary

✅ **Completed**:
- Custom 404 error page with mission-themed design
- Clear navigation options on error pages
- Backend API error responses with consistent format
- Frontend API error handling utilities

🔄 **Recommended Next Steps**:
- Add health check endpoint: `/api/v1/health/`
- Implement custom exception handler
- Add API request validation
- Set up error tracking (Sentry)
- Create offline fallback page
- Add rate limiting
- Implement circuit breaker for resilience

---

## Related Files

- Frontend: `frontend/src/pages/404.astro`
- API Utils: `frontend/src/lib/api.ts`
- Backend Views: `backend/apps/missions/views.py`
- Settings: `backend/config/settings.py`
- Docker: `docker-compose.yml`, `docker-entrypoint.sh`
