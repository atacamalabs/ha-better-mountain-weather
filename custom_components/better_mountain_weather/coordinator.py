"""Data update coordinators for Better Mountain Weather integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api.openmeteo_client import OpenMeteoApiError, OpenMeteoClient
from .const import AROME_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class AromeCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for weather data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: OpenMeteoClient,
        location_name: str,
    ) -> None:
        """Initialize the weather coordinator.

        Args:
            hass: Home Assistant instance
            client: Open-Meteo API client
            location_name: Name of the location for logging
        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{location_name}_arome",
            update_interval=AROME_UPDATE_INTERVAL,
        )
        self.client = client
        self.location_name = location_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Open-Meteo API.

        Returns:
            Dictionary containing all weather data

        Raises:
            UpdateFailed: If update fails
        """
        try:
            _LOGGER.debug("Updating weather data for %s", self.location_name)

            # Fetch all data in parallel where possible
            current_weather = await self.client.async_get_current_weather()
            daily_forecast = await self.client.async_get_daily_forecast()
            hourly_forecast = await self.client.async_get_hourly_forecast()
            hourly_6h = await self.client.async_get_hourly_6h()
            additional_data = await self.client.async_get_additional_data()

            # Combine all data
            data = {
                "current": current_weather,
                "daily_forecast": daily_forecast,
                "hourly_forecast": hourly_forecast,
                "hourly_6h": hourly_6h,
                "elevation": additional_data.get("elevation", 0),
            }

            _LOGGER.debug(
                "Successfully updated weather data for %s: %d daily forecasts, %d hourly forecasts, %d hourly 6h",
                self.location_name,
                len(daily_forecast),
                len(hourly_forecast),
                len(hourly_6h),
            )

            return data

        except OpenMeteoApiError as err:
            _LOGGER.error("Error fetching weather data for %s: %s", self.location_name, err)
            raise UpdateFailed(f"Error fetching weather data: {err}") from err
        except Exception as err:
            _LOGGER.error(
                "Unexpected error fetching weather data for %s: %s",
                self.location_name,
                err,
            )
            raise UpdateFailed(f"Unexpected error: {err}") from err


class BraCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for BRA avalanche bulletin updates.

    This will be implemented in Phase 2.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        # client: BraClient,  # Phase 2
        location_name: str,
        massif_id: str,
    ) -> None:
        """Initialize the BRA coordinator.

        Args:
            hass: Home Assistant instance
            location_name: Name of the location for logging
            massif_id: ID of the massif
        """
        from .const import BRA_UPDATE_INTERVAL

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{location_name}_bra",
            update_interval=BRA_UPDATE_INTERVAL,
        )
        # self.client = client  # Phase 2
        self.location_name = location_name
        self.massif_id = massif_id

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from BRA API.

        This will be implemented in Phase 2.

        Returns:
            Dictionary containing BRA avalanche data

        Raises:
            UpdateFailed: If update fails
        """
        # Phase 2: Implement BRA data fetching
        _LOGGER.debug("BRA coordinator not yet implemented (Phase 2)")
        return {}
