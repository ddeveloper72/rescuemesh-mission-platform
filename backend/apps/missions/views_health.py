"""
Health Check Views

Simple health check endpoint for monitoring, load balancers, and Docker health checks.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
import time


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint.
    
    **Endpoint:** GET /api/v1/health/
    
    Returns service health status including database connectivity.
    Used by Docker healthchecks, load balancers, and monitoring systems.
    
    **Response:**
    ```json
    {
      "status": "healthy",
      "timestamp": "2026-06-01T16:30:00Z",
      "checks": {
        "database": "ok",
        "cache": "ok"
      }
    }
    ```
    
    **Status Codes:**
    - 200: Service is healthy
    - 503: Service is unhealthy (database down, etc.)
    """
    checks = {}
    overall_status = "healthy"
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        overall_status = "unhealthy"
    
    # Check cache (if configured)
    try:
        test_key = "health_check_test"
        cache.set(test_key, "ok", timeout=1)
        if cache.get(test_key) == "ok":
            checks["cache"] = "ok"
        else:
            checks["cache"] = "error: cache read failed"
    except Exception as e:
        checks["cache"] = f"error: {str(e)}"
        # Cache failure is not critical, don't mark as unhealthy
    
    response_data = {
        "status": overall_status,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "checks": checks
    }
    
    http_status = status.HTTP_200_OK if overall_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(response_data, status=http_status)


@api_view(['GET'])
def readiness_check(request):
    """
    Readiness check endpoint.
    
    **Endpoint:** GET /api/v1/ready/
    
    Returns whether the service is ready to accept traffic.
    More strict than health check - ensures all dependencies are available.
    
    **Response:**
    ```json
    {
      "ready": true,
      "timestamp": "2026-06-01T16:30:00Z"
    }
    ```
    """
    # Could add more checks here like:
    # - Are migrations up to date?
    # - Are required data fixtures loaded?
    # - Are external services reachable?
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        ready = True
    except Exception:
        ready = False
    
    return Response({
        "ready": ready,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }, status=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE)
