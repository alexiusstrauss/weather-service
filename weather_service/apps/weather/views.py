"""
Weather app views - Presentation layer.
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from loguru import logger
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import WeatherHistorySerializer, WeatherRequestSerializer, WeatherResponseSerializer
from .services import WeatherServiceException
from .usecases import GetWeatherHistoryUseCase, GetWeatherUseCase, InvalidateCacheUseCase


class WeatherView(APIView):
    """
    API endpoint for getting current weather data.
    """

    @extend_schema(
        summary="Get current weather",
        description="Get current weather information for a city with caching support",
        parameters=[
            OpenApiParameter(
                name="city",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="City name to get weather for",
            ),
        ],
        responses={
            200: WeatherResponseSerializer,
            400: {"description": "Bad request - invalid city name"},
            404: {"description": "City not found"},
            429: {"description": "Rate limit exceeded"},
            500: {"description": "Internal server error"},
        },
        tags=["Weather"],
    )
    def get(self, request):
        """
        Get current weather for a city.

        Query Parameters:
        - city: City name (required)

        Returns weather data with caching information.
        """

        serializer = WeatherRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {"error": "Parâmetros inválidos", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        city = serializer.validated_data["city"]
        ip_address = self._get_client_ip(request)

        use_case = GetWeatherUseCase()

        try:
            weather_data = use_case.execute(city, ip_address)
            response_serializer = WeatherResponseSerializer(weather_data)

            logger.info(f"Weather request successful for {city} from IP {ip_address}")
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except WeatherServiceException as e:
            logger.warning(f"Weather service error for {city}: {e}")

            if "não encontrada" in str(e).lower():
                return Response({"error": "Cidade não encontrada", "message": str(e)}, status=status.HTTP_404_NOT_FOUND)

            return Response(
                {"error": "Erro no serviço de clima", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Unexpected error in weather view: {e}")
            return Response({"error": "Erro interno do servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class WeatherHistoryView(APIView):
    """
    API endpoint for getting weather query history.
    """

    @extend_schema(
        summary="Get weather query history",
        description="Get the last weather queries for a city from the current IP",
        parameters=[
            OpenApiParameter(
                name="city",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="City name to get history for",
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Maximum number of history entries (default: 10, max: 50)",
            ),
        ],
        responses={
            200: WeatherHistorySerializer,
            400: {"description": "Bad request - invalid parameters"},
            500: {"description": "Internal server error"},
        },
        tags=["Weather"],
    )
    def get(self, request):
        """
        Get weather query history for a city.

        Query Parameters:
        - city: City name (required)
        - limit: Maximum number of entries (optional, default: 10, max: 50)

        Returns the last weather queries for the city from the current IP.
        """

        city = request.query_params.get("city")
        if not city:
            return Response({"error": "Parâmetro city é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            limit = int(request.query_params.get("limit", 10))
            if limit < 1 or limit > 50:
                limit = 10
        except (ValueError, TypeError):
            limit = 10

        city = city.strip().title()
        ip_address = self._get_client_ip(request)

        use_case = GetWeatherHistoryUseCase()

        try:
            history_data = use_case.execute(city, ip_address, limit)
            response_serializer = WeatherHistorySerializer(history_data)

            logger.info(f"Weather history request successful for {city} from IP {ip_address}")
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except WeatherServiceException as e:
            logger.error(f"Weather history error for {city}: {e}")
            return Response(
                {"error": "Erro ao buscar histórico", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Unexpected error in weather history view: {e}")
            return Response({"error": "Erro interno do servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class WeatherCacheView(APIView):
    """
    API endpoint for cache management (admin only).
    """

    @extend_schema(
        summary="Invalidate weather cache",
        description="Invalidate cached weather data for a city (admin only)",
        parameters=[
            OpenApiParameter(
                name="city",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="City name to invalidate cache for",
            ),
        ],
        responses={
            200: {"description": "Cache invalidated successfully"},
            400: {"description": "Bad request - invalid city name"},
            500: {"description": "Internal server error"},
        },
        tags=["Admin"],
    )
    def delete(self, request):
        """
        Invalidate cache for a city.

        Query Parameters:
        - city: City name (required)

        This endpoint is intended for administrative use.
        """
        city = request.query_params.get("city")
        if not city:
            return Response({"error": "Parâmetro city é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

        city = city.strip().title()

        use_case = InvalidateCacheUseCase()

        try:
            use_case.execute(city)

            logger.info(f"Cache invalidated for {city}")
            return Response({"message": f"Cache invalidado para {city}"}, status=status.HTTP_200_OK)

        except WeatherServiceException as e:
            logger.error(f"Cache invalidation error for {city}: {e}")
            return Response(
                {"error": "Erro ao invalidar cache", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Unexpected error in cache invalidation: {e}")
            return Response({"error": "Erro interno do servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
