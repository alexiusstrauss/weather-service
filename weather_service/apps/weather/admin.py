"""
Weather app admin configuration.
"""
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import WeatherCache, WeatherQuery


@admin.register(WeatherQuery)
class WeatherQueryAdmin(admin.ModelAdmin):
    """Admin interface for WeatherQuery model."""

    list_display = [
        "city",
        "ip_address",
        "temperature_display",
        "description",
        "country",
        "created_at_display",
    ]

    list_filter = [
        "country",
        "created_at",
        "city",
    ]

    search_fields = [
        "city",
        "ip_address",
        "description",
    ]

    readonly_fields = [
        "created_at",
        "weather_details",
    ]

    ordering = ["-created_at"]

    list_per_page = 50

    fieldsets = (
        ("Localização", {"fields": ("city", "country", "ip_address")}),
        ("Dados Meteorológicos", {"fields": ("temperature", "description", "humidity", "pressure", "wind_speed")}),
        ("Metadados", {"fields": ("created_at", "weather_details"), "classes": ("collapse",)}),
    )

    def temperature_display(self, obj):
        """Display temperature with unit."""
        return f"{obj.temperature}°C"

    temperature_display.short_description = "Temperatura"
    temperature_display.admin_order_field = "temperature"

    def created_at_display(self, obj):
        """Display formatted creation date."""
        return obj.created_at.strftime("%d/%m/%Y %H:%M")

    created_at_display.short_description = "Data/Hora"
    created_at_display.admin_order_field = "created_at"

    def weather_details(self, obj):
        """Display detailed weather information."""
        details = []
        if obj.humidity:
            details.append(f"Umidade: {obj.humidity}%")
        if obj.pressure:
            details.append(f"Pressão: {obj.pressure} hPa")
        if obj.wind_speed:
            details.append(f"Vento: {obj.wind_speed} m/s")

        return " | ".join(details) if details else "N/A"

    weather_details.short_description = "Detalhes"

    actions = ["delete_selected"]

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related()


@admin.register(WeatherCache)
class WeatherCacheAdmin(admin.ModelAdmin):
    """Admin interface for WeatherCache model."""

    list_display = [
        "city",
        "created_at_display",
        "expires_at_display",
        "is_expired_display",
        "data_preview",
    ]

    list_filter = [
        "created_at",
        "expires_at",
    ]

    search_fields = [
        "city",
    ]

    readonly_fields = [
        "created_at",
        "is_expired",
        "formatted_data",
    ]

    ordering = ["-created_at"]

    list_per_page = 50

    fieldsets = (
        ("Cache Info", {"fields": ("city", "created_at", "expires_at", "is_expired")}),
        ("Data", {"fields": ("formatted_data",), "classes": ("collapse",)}),
    )

    def created_at_display(self, obj):
        """Display formatted creation date."""
        return obj.created_at.strftime("%d/%m/%Y %H:%M")

    created_at_display.short_description = "Criado em"
    created_at_display.admin_order_field = "created_at"

    def expires_at_display(self, obj):
        """Display formatted expiration date."""
        return obj.expires_at.strftime("%d/%m/%Y %H:%M")

    expires_at_display.short_description = "Expira em"
    expires_at_display.admin_order_field = "expires_at"

    def is_expired_display(self, obj):
        """Display expiration status with color."""
        if obj.is_expired:
            return format_html('<span style="color: red; font-weight: bold;">Expirado</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">Válido</span>')

    is_expired_display.short_description = "Status"

    def data_preview(self, obj):
        """Display preview of cached data."""
        if obj.data:
            temp = obj.data.get("temperature", "N/A")
            desc = obj.data.get("description", "N/A")
            return f"{temp}°C - {desc}"
        return "N/A"

    data_preview.short_description = "Preview"

    def formatted_data(self, obj):
        """Display formatted JSON data."""
        if obj.data:
            import json

            return format_html("<pre>{}</pre>", json.dumps(obj.data, indent=2, ensure_ascii=False))
        return "N/A"

    formatted_data.short_description = "Dados JSON"

    actions = ["delete_expired", "delete_selected"]

    def delete_expired(self, request, queryset):
        """Action to delete expired cache entries."""
        expired_count = queryset.filter(expires_at__lt=timezone.now()).count()
        queryset.filter(expires_at__lt=timezone.now()).delete()

        self.message_user(request, f"{expired_count} entradas de cache expiradas foram removidas.")

    delete_expired.short_description = "Remover entradas expiradas"
