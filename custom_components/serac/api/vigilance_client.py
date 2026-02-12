"""Météo-France Vigilance API client for weather alerts."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from ..const import DEPARTMENT_BOUNDARIES, VIGILANCE_COLOR_CODES, VIGILANCE_PHENOMENA

_LOGGER = logging.getLogger(__name__)


class VigilanceApiError(Exception):
    """Exception raised for Vigilance API errors."""


class VigilanceClient:
    """Client for Météo-France Vigilance API."""

    def __init__(
        self, api_token: str, latitude: float, longitude: float
    ) -> None:
        """Initialize the Vigilance client.

        Args:
            api_token: Météo-France Vigilance API token
            latitude: Location latitude
            longitude: Location longitude
        """
        self._api_token = api_token
        self._latitude = latitude
        self._longitude = longitude
        self._base_url = "https://public-api.meteofrance.fr/public/DPVigilance/v1"
        self._department = self._get_department_code(latitude, longitude)

    def _get_department_code(self, lat: float, lon: float) -> str | None:
        """Get French department code from GPS coordinates.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Two-digit department code (e.g., "74" for Haute-Savoie) or None if not found
        """
        # Check all department boundaries
        for dept_code, dept_info in DEPARTMENT_BOUNDARIES.items():
            bounds = dept_info["bounds"]
            min_lat, max_lat, min_lon, max_lon = bounds

            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                _LOGGER.debug(
                    "Coordinates (%.4f, %.4f) matched department %s (%s)",
                    lat,
                    lon,
                    dept_code,
                    dept_info["name"],
                )
                return dept_code

        # No match found
        _LOGGER.warning(
            "No French department found for coordinates (%.4f, %.4f). "
            "Vigilance alerts are only available for locations in France.",
            lat,
            lon,
        )
        return None

    async def async_get_current_vigilance(self) -> dict[str, Any]:
        """Get current vigilance alerts for the department.

        Returns:
            Dictionary with vigilance data:
            {
                "has_data": bool,
                "department": str,
                "department_name": str,
                "overall_level": int (1-4),
                "overall_color": str ("green", "yellow", "orange", "red"),
                "phenomena": {
                    "wind": {"level": int, "color": str},
                    "rain_flood": {"level": int, "color": str},
                    ...
                },
                "update_time": str (ISO format),
            }
        """
        # Check if coordinates are in France
        if not self._department:
            return {
                "has_data": False,
                "error": "not_in_france",
                "message": "Vigilance alerts only available for French locations",
            }

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"apikey": self._api_token}
                url = f"{self._base_url}/cartevigilance/encours"

                _LOGGER.debug(
                    "Fetching vigilance data for department %s from %s",
                    self._department,
                    url,
                )

                async with session.get(
                    url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # DEBUG: Log the full API response to understand structure
                    import json
                    _LOGGER.warning(
                        "VIGILANCE API RESPONSE (dept %s): %s",
                        self._department,
                        json.dumps(data, indent=2, ensure_ascii=False)
                    )

                    _LOGGER.debug(
                        "Vigilance API response received for department %s",
                        self._department,
                    )

                    # Extract data for our department
                    department_data = self._extract_department_data(data)

                    if not department_data:
                        _LOGGER.warning(
                            "No vigilance data found for department %s in API response",
                            self._department,
                        )
                        return {
                            "has_data": False,
                            "department": self._department,
                            "error": "no_data",
                        }

                    result = {
                        "has_data": True,
                        "department": self._department,
                        "department_name": DEPARTMENT_BOUNDARIES.get(
                            self._department, {}
                        ).get("name", "Unknown"),
                        "overall_level": department_data.get("overall_level", 1),
                        "overall_color": VIGILANCE_COLOR_CODES.get(
                            department_data.get("overall_level", 1), "green"
                        ),
                        "phenomena": department_data.get("phenomena", {}),
                        "update_time": data.get("update_time"),
                    }

                    _LOGGER.info(
                        "Vigilance data for %s (%s): level %d (%s), %d phenomena",
                        self._department,
                        result["department_name"],
                        result["overall_level"],
                        result["overall_color"],
                        len(result["phenomena"]),
                    )

                    return result

        except aiohttp.ClientResponseError as err:
            if err.status == 404:
                _LOGGER.warning(
                    "No vigilance data available for department %s (404 Not Found)",
                    self._department,
                )
                return {
                    "has_data": False,
                    "department": self._department,
                    "error": "not_found",
                }
            elif err.status in (401, 403):
                _LOGGER.error(
                    "Authentication failed for Vigilance API (status %d). "
                    "Check that your Vigilance API token is valid.",
                    err.status,
                )
                raise VigilanceApiError(
                    f"Authentication error: {err.status}"
                ) from err
            else:
                _LOGGER.error(
                    "HTTP error %d getting vigilance data: %s",
                    err.status,
                    err,
                    exc_info=True,
                )
                raise VigilanceApiError(f"HTTP error: {err}") from err

        except aiohttp.ClientError as err:
            _LOGGER.error(
                "Network error getting vigilance data: %s", err, exc_info=True
            )
            raise VigilanceApiError(f"Network error: {err}") from err

        except Exception as err:
            _LOGGER.error(
                "Unexpected error getting vigilance data: %s", err, exc_info=True
            )
            raise VigilanceApiError(f"Failed to get vigilance: {err}") from err

    def _extract_department_data(self, data: dict) -> dict | None:
        """Extract vigilance data for specific department from API response.

        Args:
            data: Full API response from Vigilance API

        Returns:
            Department-specific vigilance data or None if not found
        """
        # The actual API response structure may vary - this is a template
        # that should be adjusted based on the real API response format

        # Typical structure might be:
        # {
        #   "product": {
        #     "update_time": "2026-02-12T10:00:00Z",
        #     "timelaps": [
        #       {
        #         "timelaps_id": 1,
        #         "begin_time": "2026-02-12T06:00:00Z",
        #         "end_time": "2026-02-13T06:00:00Z",
        #         "zones": {
        #           "74": {
        #             "niveau_vigilance": 2,
        #             "phenomenes": {
        #               "1": {"niveau": 2},  # wind
        #               "5": {"niveau": 1},  # snow_ice
        #               ...
        #             }
        #           }
        #         }
        #       }
        #     ]
        #   }
        # }

        try:
            # Navigate to department data (adjust path based on real API)
            product = data.get("product", {})
            timelaps_list = product.get("timelaps", [])

            if not timelaps_list:
                _LOGGER.debug("No timelaps data in vigilance response")
                return None

            # Get current/first timelaps
            current_timelaps = timelaps_list[0]
            zones = current_timelaps.get("zones", {})
            dept_data = zones.get(self._department, zones.get(str(self._department)))

            if not dept_data:
                _LOGGER.debug(
                    "Department %s not found in zones: %s",
                    self._department,
                    list(zones.keys()),
                )
                return None

            # Extract overall level
            overall_level = dept_data.get("niveau_vigilance", 1)

            # Extract individual phenomena
            phenomena = {}
            phenomenes_data = dept_data.get("phenomenes", {})

            for phenom_id, phenom_data in phenomenes_data.items():
                # Convert phenomenon ID to name
                phenom_id_int = int(phenom_id)
                phenom_name = VIGILANCE_PHENOMENA.get(phenom_id_int)

                if phenom_name:
                    phenom_level = phenom_data.get("niveau", 1)
                    phenomena[phenom_name] = {
                        "level": phenom_level,
                        "color": VIGILANCE_COLOR_CODES.get(phenom_level, "green"),
                    }

            return {
                "overall_level": overall_level,
                "phenomena": phenomena,
            }

        except (KeyError, ValueError, TypeError) as err:
            _LOGGER.error(
                "Error parsing vigilance data for department %s: %s",
                self._department,
                err,
                exc_info=True,
            )
            return None
