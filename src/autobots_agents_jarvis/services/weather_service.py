# ABOUTME: Weather service — mock implementation for demonstration purposes.
# ABOUTME: Provides synthetic weather data for various locations.

import random
from typing import Any

# Mock weather database with synthetic data
WEATHER_DATA: dict[str, dict[str, Any]] = {
    "san francisco": {
        "location": "San Francisco",
        "temperature": {"value": 62, "unit": "fahrenheit"},
        "conditions": "Foggy",
    },
    "new york": {
        "location": "New York",
        "temperature": {"value": 55, "unit": "fahrenheit"},
        "conditions": "Partly Cloudy",
    },
    "london": {
        "location": "London",
        "temperature": {"value": 12, "unit": "celsius"},
        "conditions": "Rainy",
    },
    "tokyo": {
        "location": "Tokyo",
        "temperature": {"value": 18, "unit": "celsius"},
        "conditions": "Clear",
    },
    "seattle": {
        "location": "Seattle",
        "temperature": {"value": 50, "unit": "fahrenheit"},
        "conditions": "Rainy",
    },
    "miami": {
        "location": "Miami",
        "temperature": {"value": 82, "unit": "fahrenheit"},
        "conditions": "Sunny",
    },
}

# Forecast templates for different conditions
FORECAST_TEMPLATES: dict[str, list[str]] = {
    "Foggy": ["Foggy morning clearing to partly cloudy", "Continued fog with light winds", "Fog dissipating by midday"],
    "Partly Cloudy": ["Mostly sunny", "Increasing clouds", "Cloudy with chance of rain"],
    "Rainy": ["Light rain continuing", "Heavy rain expected", "Rain tapering off", "Scattered showers"],
    "Clear": ["Clear skies continuing", "Partly cloudy", "Mostly sunny", "Clear and pleasant"],
    "Sunny": ["Sunny and warm", "Hot and sunny", "Clear skies", "Bright sunshine"],
}


def get_weather(location: str) -> dict[str, Any]:
    """Get current weather information for a location.

    Args:
        location: The location to get weather for (e.g., "San Francisco", "New York")

    Returns:
        A dictionary containing location, temperature, and conditions
    """
    location_key = location.lower()

    if location_key not in WEATHER_DATA:
        return {"error": f"Weather data not available for '{location}'. Try: San Francisco, New York, London, Tokyo, Seattle, or Miami."}

    return WEATHER_DATA[location_key].copy()


def get_forecast(location: str, days: int = 3) -> dict[str, Any]:
    """Get weather forecast for a location.

    Args:
        location: The location to get forecast for
        days: Number of days to forecast (default: 3, max: 7)

    Returns:
        A dictionary containing location and forecast array
    """
    location_key = location.lower()

    if location_key not in WEATHER_DATA:
        return {"error": f"Weather data not available for '{location}'. Try: San Francisco, New York, London, Tokyo, Seattle, or Miami."}

    # Limit days to reasonable range
    days = min(max(days, 1), 7)

    # Get current conditions and generate forecast based on it
    current = WEATHER_DATA[location_key]
    conditions = current["conditions"]
    forecast_options = FORECAST_TEMPLATES.get(conditions, ["Conditions vary"])

    # Generate forecast days
    forecast_list = []
    for i in range(days):
        # Rotate through forecast options with some randomness
        forecast_list.append(random.choice(forecast_options))

    return {
        "location": current["location"],
        "forecast": forecast_list,
    }
