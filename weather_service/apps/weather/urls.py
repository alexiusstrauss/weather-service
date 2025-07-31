"""
Weather app URLs.
"""
from django.urls import path

from . import views

app_name = "weather"

urlpatterns = [
    path("weather/", views.WeatherView.as_view(), name="weather"),
    path("weather/history/", views.WeatherHistoryView.as_view(), name="weather-history"),
    path("weather/cache/", views.WeatherCacheView.as_view(), name="weather-cache"),
]
