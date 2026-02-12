"""Binary sensor platform for Serac integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_ENTITY_PREFIX,
    CONF_LOCATION_NAME,
    DOMAIN,
    MANUFACTURER,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Serac binary sensors from a config entry."""
    location_name = entry.data[CONF_LOCATION_NAME]
    entity_prefix = entry.data[CONF_ENTITY_PREFIX]
    latitude = entry.data[CONF_LATITUDE]
    longitude = entry.data[CONF_LONGITUDE]

    entities = []

    # Add vigilance binary sensors if coordinator exists
    vigilance_coordinator = hass.data[DOMAIN][entry.entry_id].get("vigilance_coordinator")
    if vigilance_coordinator:
        # Has Active Alert (any alert > green/level 1)
        entities.append(VigilanceAlertBinarySensor(
            vigilance_coordinator,
            location_name,
            entity_prefix,
            latitude,
            longitude,
            "has_active_alert",
            "Active Alert",
            "mdi:alert-circle",
        ))

        # Has Orange Alert (any alert >= orange/level 3)
        entities.append(VigilanceAlertBinarySensor(
            vigilance_coordinator,
            location_name,
            entity_prefix,
            latitude,
            longitude,
            "has_orange_alert",
            "Orange Alert",
            "mdi:alert",
        ))

        # Has Red Alert (any alert = red/level 4)
        entities.append(VigilanceAlertBinarySensor(
            vigilance_coordinator,
            location_name,
            entity_prefix,
            latitude,
            longitude,
            "has_red_alert",
            "Red Alert",
            "mdi:alert-octagon",
        ))

    async_add_entities(entities, True)


class VigilanceAlertBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for Météo-France Vigilance weather alerts."""

    _attr_has_entity_name = False
    _attr_attribution = "Data from Météo-France Vigilance"
    _attr_device_class = BinarySensorDeviceClass.SAFETY

    def __init__(
        self,
        coordinator,
        location_name: str,
        entity_prefix: str,
        latitude: float,
        longitude: float,
        sensor_type: str,
        sensor_name: str,
        icon: str,
    ) -> None:
        """Initialize the vigilance binary sensor."""
        super().__init__(coordinator)
        self._location_name = location_name
        self._entity_prefix = entity_prefix
        self._latitude = latitude
        self._longitude = longitude
        self._sensor_type = sensor_type
        self._attr_icon = icon

        # Sanitize entity_prefix for entity_id
        import re
        import unicodedata

        safe_prefix = self._sanitize_entity_id_part(entity_prefix)

        # Set entity_id: binary_sensor.serac_{prefix}_{type}
        self.entity_id = f"binary_sensor.serac_{safe_prefix}_{sensor_type}"

        # Unique ID uses coordinates and sensor type
        self._attr_unique_id = f"serac_{latitude}_{longitude}_{sensor_type}"

        # Set friendly name
        self._attr_name = f"Serac {entity_prefix.title()} {sensor_name}"

    @staticmethod
    def _sanitize_entity_id_part(text: str) -> str:
        """Sanitize text for use in entity IDs."""
        import re
        import unicodedata

        # Normalize unicode characters (decompose accents)
        text = unicodedata.normalize('NFKD', text)
        # Remove diacritics (accent marks)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        # Convert to lowercase
        text = text.lower()
        # Replace any non-alphanumeric characters (except underscore) with underscore
        text = re.sub(r'[^a-z0-9_]+', '_', text)
        # Remove multiple consecutive underscores
        text = re.sub(r'_+', '_', text)
        # Remove leading/trailing underscores
        text = text.strip('_')

        return text

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"serac_{self._latitude}_{self._longitude}")},
            name=f"{self._location_name} (Serac)",
            manufacturer=MANUFACTURER,
            model="Weather & Avalanche Data",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        if not self.coordinator.data or not self.coordinator.data.get("has_data"):
            return False

        phenomena = self.coordinator.data.get("phenomena", {})
        if not phenomena:
            return False

        if self._sensor_type == "has_active_alert":
            # Check if any phenomenon has level > 1 (green)
            for phenom_data in phenomena.values():
                if phenom_data.get("level", 1) > 1:
                    return True
            return False

        elif self._sensor_type == "has_orange_alert":
            # Check if any phenomenon has level >= 3 (orange)
            for phenom_data in phenomena.values():
                if phenom_data.get("level", 1) >= 3:
                    return True
            return False

        elif self._sensor_type == "has_red_alert":
            # Check if any phenomenon has level = 4 (red)
            for phenom_data in phenomena.values():
                if phenom_data.get("level", 1) == 4:
                    return True
            return False

        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("has_data"):
            return {}

        attrs = {
            "department": self.coordinator.data.get("department"),
            "department_name": self.coordinator.data.get("department_name"),
            "overall_level": self.coordinator.data.get("overall_level"),
            "overall_color": self.coordinator.data.get("overall_color"),
        }

        # Add list of active alerts for this binary sensor type
        phenomena = self.coordinator.data.get("phenomena", {})
        active_alerts = []

        if self._sensor_type == "has_active_alert":
            # List all non-green alerts
            for phenom_name, phenom_data in phenomena.items():
                if phenom_data.get("level", 1) > 1:
                    active_alerts.append({
                        "phenomenon": phenom_name,
                        "level": phenom_data.get("level"),
                        "color": phenom_data.get("color"),
                    })

        elif self._sensor_type == "has_orange_alert":
            # List all orange and red alerts
            for phenom_name, phenom_data in phenomena.items():
                if phenom_data.get("level", 1) >= 3:
                    active_alerts.append({
                        "phenomenon": phenom_name,
                        "level": phenom_data.get("level"),
                        "color": phenom_data.get("color"),
                    })

        elif self._sensor_type == "has_red_alert":
            # List only red alerts
            for phenom_name, phenom_data in phenomena.items():
                if phenom_data.get("level", 1) == 4:
                    active_alerts.append({
                        "phenomenon": phenom_name,
                        "level": phenom_data.get("level"),
                        "color": phenom_data.get("color"),
                    })

        if active_alerts:
            attrs["active_alerts"] = active_alerts
            attrs["alert_count"] = len(active_alerts)

        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Binary sensor is available if coordinator succeeded and has data
        if not self.coordinator.last_update_success:
            return False

        # If data exists but has_data is False (not in France), mark unavailable
        if self.coordinator.data and not self.coordinator.data.get("has_data"):
            return False

        return True
