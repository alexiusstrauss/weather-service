"""
URL configuration for weather_service project.
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Core endpoints
    path("", include("weather_service.apps.core.urls")),
    # Weather endpoints
    path("api/v1/", include("weather_service.apps.weather.urls")),
    # Prometheus metrics
    path("", include("django_prometheus.urls")),
]
