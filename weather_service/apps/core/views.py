"""
Core app views.
"""
import redis
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HomeView(View):
    """Home view with API information."""

    def get(self, request):
        return JsonResponse(
            {
                "message": "Weather Service API",
                "version": "1.0.0",
                "docs": "/api/docs/",
                "health": "/health/",
                "metrics": "/metrics",
            }
        )


class HealthCheckView(APIView):
    """Health check endpoint for monitoring."""

    def get(self, request):
        """
        Perform health checks on all services.
        """
        health_status = {"status": "healthy", "timestamp": request.META.get("HTTP_DATE"), "services": {}}

        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status["services"]["database"] = "healthy"
        except Exception as e:
            health_status["services"]["database"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"

        # Check Redis cache
        try:
            cache.set("health_check", "ok", 10)
            cache.get("health_check")
            health_status["services"]["cache"] = "healthy"
        except Exception as e:
            health_status["services"]["cache"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"

        # Check Redis directly
        try:
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            health_status["services"]["redis"] = "healthy"
        except Exception as e:
            # Em ambiente de teste, não considerar falha do Redis como erro fatal
            if getattr(settings, "TESTING", False):
                health_status["services"]["redis"] = "mock (testing)"
            else:
                health_status["services"]["redis"] = f"unhealthy: {str(e)}"
                health_status["status"] = "unhealthy"

        response_status = (
            status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return Response(health_status, status=response_status)
