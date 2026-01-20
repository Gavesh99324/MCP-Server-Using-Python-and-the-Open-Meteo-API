from typing import Any
import math
import urllib.parse

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
OPENMETEO_API_BASE = "https://api.open-meteo.com/v1"
OPENMETEO_GEOCODING_BASE = "https://geocoding-api.open-meteo.com/v1"
USER_AGENT = "weather-app/1.0"


async def make_openmeteo_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Open-Meteo API with basic error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


@mcp.tool()
async def get_current_weather(latitude: float, longitude: float) -> dict[str, Any] | str:
    """Get current weather for a location using latitude and longitude."""

    query = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,is_day,showers,cloud_cover,wind_speed_10m,"
            "wind_direction_10m,pressure_msl,snowfall,precipitation,"
            "relative_humidity_2m,apparent_temperature,rain,weather_code,"
            "surface_pressure,wind_gusts_10m"
        ),
        "timezone": "auto",
    }
    url = f"{OPENMETEO_API_BASE}/forecast?{urllib.parse.urlencode(query, safe=',')}"
    data = await make_openmeteo_request(url)

    if not data:
        return "Unable to fetch current weather data for this location."

    return data


@mcp.tool()
async def get_forecast(
    latitude: float,
    longitude: float,
    hours: int = 24,
) -> dict[str, Any] | str:
    """Get an hourly forecast for the next N hours (1-168)."""

    forecast_hours = max(1, min(hours, 168))
    forecast_days = max(1, math.ceil(forecast_hours / 24))

    hourly_params = [
        "temperature_2m",
        "apparent_temperature",
        "precipitation",
        "rain",
        "snowfall",
        "cloud_cover",
        "wind_speed_10m",
        "wind_direction_10m",
        "weather_code",
        "relative_humidity_2m",
        "surface_pressure",
    ]

    query = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(hourly_params),
        "forecast_days": forecast_days,
        "timezone": "auto",
    }

    url = f"{OPENMETEO_API_BASE}/forecast?{urllib.parse.urlencode(query, safe=',')}"
    data = await make_openmeteo_request(url)

    if not data:
        return "Unable to fetch forecast data for this location."

    if forecast_hours < forecast_days * 24:
        # Trim extra hours so the caller only sees the requested window.
        try:
            data = data.copy()
            for key in list(data.get("hourly", {}).keys()):
                series = data["hourly"][key]
                if isinstance(series, list):
                    data["hourly"][key] = series[:forecast_hours]
        except Exception:
            # If trimming fails, return the untrimmed payload.
            pass

    return data


@mcp.tool()
async def get_location(query: str, count: int = 5) -> dict[str, Any] | str:
    """Search for a location by name using Open-Meteo Geocoding."""

    safe_count = max(1, min(count, 10))
    encoded_query = urllib.parse.quote_plus(query.strip())
    url = (
        f"{OPENMETEO_GEOCODING_BASE}/search?name={encoded_query}"
        f"&count={safe_count}&language=en&format=json"
    )

    data = await make_openmeteo_request(url)

    if not data:
        return "Unable to search for this location right now."

    return data


if __name__ == "__main__":
    # Start the MCP server using stdio, which is what MCP clients expect.
    mcp.run(transport="stdio")
