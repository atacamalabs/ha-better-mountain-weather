"""Open-Meteo Air Quality API client for Better Mountain Weather integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class AirQualityApiError(Exception):
    """Exception raised for Air Quality API errors."""


class AirQualityClient:
    """Client for Open-Meteo Air Quality API."""

    def __init__(self, latitude: float, longitude: float) -> None:
        """Initialize the Air Quality client.

        Args:
            latitude: Location latitude
            longitude: Location longitude
        """
        self.latitude = latitude
        self.longitude = longitude
        self.base_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    async def async_get_air_quality(self) -> dict[str, Any]:
        """Fetch air quality data from Open-Meteo Air Quality API.

        Returns:
            Dictionary with current air quality and hourly forecast

        Raises:
            AirQualityApiError: If the API request fails
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": ",".join([
                "european_aqi",
                "pm2_5",
                "pm10",
                "nitrogen_dioxide",
                "ozone",
                "sulphur_dioxide",
            ]),
            "hourly": "european_aqi",
            "timezone": "auto",
            "forecast_days": 4,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise AirQualityApiError(
                            f"Air Quality API returned status {response.status}: {error_text}"
                        )

                    data = await response.json()

            # Extract current air quality
            current = data.get("current", {})
            current_aqi = {
                "european_aqi": current.get("european_aqi"),
                "pm2_5": current.get("pm2_5"),
                "pm10": current.get("pm10"),
                "nitrogen_dioxide": current.get("nitrogen_dioxide"),
                "ozone": current.get("ozone"),
                "sulphur_dioxide": current.get("sulphur_dioxide"),
            }

            # Extract hourly forecast (next 24 hours)
            hourly_data = data.get("hourly", {})
            hourly_times = hourly_data.get("time", [])
            hourly_aqi = hourly_data.get("european_aqi", [])

            # Limit to next 24 hours
            hourly_forecast = []
            for i in range(min(24, len(hourly_times))):
                if i < len(hourly_aqi):
                    hourly_forecast.append({
                        "datetime": hourly_times[i],
                        "european_aqi": hourly_aqi[i],
                    })

            return {
                "current": current_aqi,
                "hourly_forecast": hourly_forecast,
            }

        except aiohttp.ClientError as err:
            raise AirQualityApiError(f"Error communicating with Air Quality API: {err}") from err
        except Exception as err:
            raise AirQualityApiError(f"Unexpected error fetching air quality data: {err}") from err
