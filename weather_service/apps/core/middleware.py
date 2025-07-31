"""
Core middleware for the weather service.
"""
import prometheus_client
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from loguru import logger

# Prometheus metrics
rate_limit_counter = prometheus_client.Counter(
    "weather_service_rate_limit_blocked_total", "Total number of requests blocked by rate limiting", ["ip_address"]
)


class RateLimitMiddleware:
    """
    Rate limiting middleware using Redis.
    Blocks requests exceeding configured limits per IP.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_limit = getattr(settings, "RATE_LIMIT_REQUESTS", 5)
        self.window_seconds = getattr(settings, "RATE_LIMIT_WINDOW", 60)

    def __call__(self, request):
        # Skip rate limiting for health checks and metrics
        if request.path in ["/health/", "/metrics"]:
            return self.get_response(request)

        # Skip rate limiting for tests (except when explicitly enabled for BDD tests)
        if getattr(settings, "TESTING", False) and not getattr(settings, "BDD_RATE_LIMITING_ENABLED", False):
            return self.get_response(request)

        # Apply rate limiting only to weather query endpoint
        # History and cache endpoints don't need rate limiting as they query local database
        if not (request.path == "/api/v1/weather/" or request.path.startswith("/api/v1/weather/?")):
            return self.get_response(request)

        # Get client IP
        ip_address = self.get_client_ip(request)

        # Check rate limit
        if self.is_rate_limited(ip_address):
            rate_limit_counter.labels(ip_address=ip_address).inc()
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")

            return JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_limit} requests per {self.window_seconds} seconds allowed",
                    "retry_after": self.window_seconds,
                },
                status=429,
            )

        # Record the request
        self.record_request(ip_address)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def is_rate_limited(self, ip_address):
        """Check if the IP address has exceeded the rate limit."""
        cache_key = f"rate_limit:{ip_address}"
        current_requests = cache.get(cache_key, 0)
        return current_requests >= self.requests_limit

    def record_request(self, ip_address):
        """Record a request for the IP address."""
        cache_key = f"rate_limit:{ip_address}"
        current_requests = cache.get(cache_key, 0)
        cache.set(cache_key, current_requests + 1, self.window_seconds)
