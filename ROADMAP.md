# Serac Development Roadmap - Post v1.1.0

## Context

Serac v1.1.0 has been successfully released with:
- Complete rebrand from "Better Mountain Weather" to "Serac"
- Smart entity naming with user-defined prefixes
- All 35 French massifs supported (Alps, Pyrenees, Corsica)
- 3-step config flow (location → prefix → massifs)
- Comprehensive documentation and migration guide

The user has asked for a development plan covering what should be built next and how to approach implementation.

**Current Limitation**: Users cannot change their massif selection or BRA token without completely removing and re-adding the integration. This is the biggest pain point preventing iteration and experimentation.

---

## Development Priorities

### Priority 1: Options Flow ⚙️ (HIGHEST VALUE)

**Why This Matters:**
- **Biggest user pain point**: Users must reinstall to change massifs or add/remove BRA token
- **Enables experimentation**: Users can try different massif combinations without losing their setup
- **Professional UX**: Matches standard Home Assistant integration patterns
- **No breaking changes**: Can be added as enhancement to existing installs

**User Value**: ⭐⭐⭐⭐⭐ (Critical improvement)
**Effort**: 🔨🔨🔨 (2-3 hours)
**Dependencies**: None (can start immediately)

#### What Needs to Be Done

1. **Add OptionsFlowHandler class** to config_flow.py
2. **Implement massif modification** - Allow users to select/deselect massifs
3. **Implement BRA token update** - Allow adding/removing/changing BRA token
4. **Handle coordinator lifecycle** - Create new BRA coordinators, remove old ones
5. **Update platforms** - Reload sensor platform to reflect changes

#### Implementation Approach

**File: `custom_components/serac/config_flow.py`**

Add OptionsFlowHandler class:
```python
@staticmethod
@callback
def async_get_options_flow(config_entry):
    """Get the options flow for this handler."""
    return SeracOptionsFlow(config_entry)

class SeracOptionsFlow(config_entries.OptionsFlow):
    """Handle Serac options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Update config entry with new massifs/token
            new_data = {**self.config_entry.data}
            new_data[CONF_MASSIF_IDS] = user_input.get(CONF_MASSIF_IDS, [])

            # Update BRA token if provided, or remove if empty
            if user_input.get(CONF_BRA_TOKEN):
                new_data[CONF_BRA_TOKEN] = user_input[CONF_BRA_TOKEN]
            elif CONF_BRA_TOKEN in new_data and not user_input.get(CONF_BRA_TOKEN):
                # User cleared token, remove it
                new_data.pop(CONF_BRA_TOKEN, None)

            # Update config entry
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )

            # Reload the integration to apply changes
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)

            return self.async_create_entry(title="", data={})

        # Get current values
        current_massifs = self.config_entry.data.get(CONF_MASSIF_IDS, [])
        current_token = self.config_entry.data.get(CONF_BRA_TOKEN, "")

        # Create massif options
        massif_options = {str(num_id): name for num_id, (name, _) in MASSIF_IDS.items()}

        data_schema = vol.Schema({
            vol.Optional(
                CONF_BRA_TOKEN,
                description="Météo-France BRA API token",
                default=current_token
            ): str,
            vol.Optional(
                CONF_MASSIF_IDS,
                description="Select massifs for avalanche bulletins",
                default=current_massifs
            ): cv.multi_select(massif_options),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            description_placeholders={
                "info": "Change your massif selection or BRA token. The integration will reload automatically."
            },
        )
```

**File: `custom_components/serac/__init__.py`**

The existing `async_reload_entry` function will handle the reload:
```python
async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
```

This already exists and will:
1. Unload all platforms (weather, sensors)
2. Remove coordinators from hass.data
3. Re-run setup with new config data
4. Create new BRA coordinators for selected massifs
5. Set up platforms with new sensors

**No entity ID changes** - Weather entities keep same entity_id (based on prefix), avalanche sensors are added/removed based on massif selection.

#### Testing Plan

1. **Install fresh Serac instance** with 2 massifs (e.g., Aravis, Mont-Blanc)
2. **Verify entities created** - Check Developer Tools → States for avalanche sensors
3. **Open Options** - Settings → Devices & Services → Serac → Configure
4. **Add a massif** (e.g., add Chablais)
5. **Verify new sensors appear** - Check for `sensor.serac_{prefix}_chablais_avalanche_risk_today`
6. **Remove a massif** (e.g., remove Mont-Blanc)
7. **Verify sensors removed** - Check Mont-Blanc sensors are gone
8. **Change BRA token** - Update to different token
9. **Verify reload** - Check logs for successful reload
10. **Remove BRA token entirely** - Clear token field
11. **Verify all avalanche sensors removed** - Only weather sensors remain

#### Strings to Add

**File: `custom_components/serac/strings.json`**
```json
{
  "options": {
    "step": {
      "init": {
        "title": "Serac Configuration",
        "description": "Change your massif selection or BRA API token. The integration will reload automatically.",
        "data": {
          "bra_token": "Météo-France BRA API Token",
          "massif_ids": "Massifs for Avalanche Bulletins"
        }
      }
    }
  }
}
```

#### Estimated Effort
- Implementation: 1.5 hours
- Testing: 1 hour
- **Total: 2-3 hours**

---

### Priority 2: Logo & Branding 🎨 (QUICK WIN)

**Why This Matters:**
- **Visual identity**: Makes Serac recognizable in HACS and Devices & Services
- **Professional appearance**: Shows polish and care
- **Branding consistency**: Reinforces "Serac" name with ice/mountain imagery
- **Quick impact**: Minimal code, maximum visual improvement

**User Value**: ⭐⭐⭐ (Nice improvement)
**Effort**: 🔨 (1-2 hours, mostly design)
**Dependencies**: Need logo design/sourcing

#### What Needs to Be Done

1. **Design or source logo** - Mountain/serac/ice themed, 256×256px PNG
2. **Add icon.png** to integration folder
3. **Update manifest.json** (if HA version supports it)
4. **Add logo to README.md** header
5. **Update HACS repository metadata**

#### Implementation Approach

**Logo Requirements:**
- **Format**: PNG with transparency
- **Size**: 256×256 pixels (Home Assistant standard)
- **Theme**: Mountain/ice/serac formation
- **Colors**: Blue/white palette (ice/snow/sky)
- **Style**: Clean, modern, recognizable at small sizes

**Logo Options:**
1. **Commission designer** - Fiverr, Upwork (~$20-50, 1-3 days)
2. **Use AI generation** - DALL-E, Midjourney (immediate, free/cheap)
3. **Find royalty-free** - Noun Project, Flaticon (immediate, free/attribution)

**Files to Create/Modify:**

1. **`custom_components/serac/icon.png`** - Add 256×256 logo
2. **`custom_components/serac/manifest.json`** - No changes needed (icon.png auto-detected)
3. **`README.md`** - Add logo to header:
   ```markdown
   <p align="center">
     <img src="https://raw.githubusercontent.com/atacamalabs/ha-serac/main/custom_components/serac/icon.png" width="200" alt="Serac Logo">
   </p>

   # Serac 🏔️
   ```

4. **`hacs.json`** - Verify logo shows in HACS (auto-detected from icon.png)

#### Testing Plan

1. Add icon.png to `custom_components/serac/`
2. Restart Home Assistant
3. Navigate to **Settings → Devices & Services**
4. Verify Serac shows custom icon (not generic puzzle piece)
5. Check HACS → Integrations → Serac for logo display
6. View README on GitHub to verify logo appears

#### Estimated Effort
- Logo design/sourcing: Variable (30 min - 3 days)
- Implementation: 15 minutes
- Testing: 15 minutes
- **Total: 1-2 hours** (assuming logo is ready)

---

### Priority 3: Enhanced Documentation 📚 (USER EXPERIENCE)

**Why This Matters:**
- **Reduces support burden**: Clear docs = fewer issues opened
- **Improves onboarding**: New users can self-serve
- **Builds trust**: Professional documentation signals quality
- **SEO benefits**: Better discoverability via searches

**User Value**: ⭐⭐⭐⭐ (Significant improvement)
**Effort**: 🔨🔨🔨 (3-4 hours)
**Dependencies**: Need screenshots from live HA instance

#### What Needs to Be Done

1. **Add screenshots** to README
   - Config flow steps (3 screenshots)
   - Weather card example
   - Sensor cards (weather + avalanche)
   - Devices & Services page showing Serac
2. **Create FAQ section** in README
3. **Expand troubleshooting guide** with common issues
4. **Add French translation** (translations/fr.json)
5. **Create CONTRIBUTING.md** for developers

#### Implementation Approach

**Screenshots to Capture:**

1. **Config Step 1** - Location input (shows coordinates, location name)
2. **Config Step 2** - Entity prefix selection (shows suggestion, validation)
3. **Config Step 3** - Massif selection (shows multi-select with all 35 massifs)
4. **Weather Card** - Lovelace weather-forecast card showing Serac data
5. **Sensor Card** - Entity list showing temperature, wind, AQI sensors
6. **Avalanche Card** - Entity list showing avalanche risk sensors for a massif
7. **Devices Page** - Settings → Devices & Services showing Serac integration

**Store screenshots in:** `docs/screenshots/` folder, reference in README

**FAQ Section (Add to README.md):**
```markdown
## Frequently Asked Questions

### Can I change my massif selection after setup?
Yes! Go to Settings → Devices & Services → Serac → Configure to add/remove massifs without reinstalling.

### Why aren't avalanche sensors appearing?
1. Verify you entered a valid BRA API token
2. Check you selected at least one massif
3. Avalanche bulletins are seasonal (~December-May) - check logs for "out of season" messages
4. Verify the BRA API is accessible from your network

### How do I get multiple locations?
Add the Serac integration multiple times with different coordinates. Use unique entity prefixes (e.g., "chamonix", "zermatt") to keep sensors organized.

### Can I use this outside France?
Weather data works worldwide (Open-Meteo). Avalanche bulletins only work for French massifs (Météo-France BRA API limitation).

### What's the difference between risk_today and risk_high_altitude?
- **risk_today/tomorrow**: Overall risk level (1-5 scale)
- **risk_high_altitude/low_altitude**: Risk at different elevation zones (text descriptions)
```

**Troubleshooting Expansion:**
```markdown
### Common Issues

#### "Cannot connect" error during setup
- **Cause**: Invalid coordinates format or network issue
- **Solution**:
  - Use decimal format (e.g., 45.9237, not 45° 55' 25")
  - Verify internet connection
  - Try known coordinates (Chamonix: 45.9237, 6.8694)

#### Weather data stops updating
- **Cause**: Open-Meteo API outage or rate limiting
- **Solution**:
  - Check Home Assistant logs: `tail -f /config/home-assistant.log | grep serac`
  - Wait 1 hour for next update attempt
  - Reload integration: Settings → Devices & Services → Serac → ⋮ → Reload

#### Avalanche sensors showing "Unknown"
- **Cause**: Out of season (May-November), invalid token, or massif with no bulletin
- **Solution**:
  - Check logs for "out of season" or API error messages
  - Verify BRA token is valid at https://portail-api.meteofrance.fr/
  - Try different massif (some publish earlier/later in season)
```

**French Translation (translations/fr.json):**
```json
{
  "config": {
    "step": {
      "user": {
        "title": "Localisation",
        "description": "Entrez le nom de votre emplacement et ses coordonnées GPS",
        "data": {
          "location_name": "Nom de l'emplacement",
          "latitude": "Latitude",
          "longitude": "Longitude"
        }
      },
      "prefix": {
        "title": "Préfixe des entités",
        "description": "Choisissez un identifiant court pour vos entités. Suggestion : {suggested_prefix}\n\nExemple : {example_entity}",
        "data": {
          "entity_prefix": "Préfixe des entités"
        }
      },
      "massifs": {
        "title": "Bulletins d'avalanche",
        "description": "Optionnel : Ajoutez votre clé API BRA Météo-France et sélectionnez les massifs. Laissez vide pour utiliser uniquement la météo.",
        "data": {
          "bra_token": "Clé API Météo-France BRA",
          "massif_ids": "Massifs pour bulletins d'avalanche"
        }
      }
    },
    "error": {
      "cannot_connect": "Échec de connexion : vérifiez vos coordonnées",
      "invalid_prefix": "Préfixe invalide. Doit commencer par une lettre et contenir uniquement des lettres minuscules, chiffres et underscores (1-20 caractères)."
    }
  }
}
```

#### Testing Plan

1. Take screenshots on test HA instance
2. Add screenshots to `docs/screenshots/` folder
3. Update README with image links
4. Add FAQ and troubleshooting sections
5. Create translations/fr.json
6. View README on GitHub to verify formatting
7. Test a real user scenario: new user follows docs from scratch

#### Estimated Effort
- Screenshots: 30 minutes
- FAQ writing: 1 hour
- Troubleshooting expansion: 1 hour
- French translation: 30 minutes
- CONTRIBUTING.md: 30 minutes
- **Total: 3-4 hours**

---

### Priority 4: Code Quality & Diagnostics 🔧 (MAINTAINABILITY)

**Why This Matters:**
- **Easier debugging**: Users can share diagnostic data with issues
- **Better error messages**: Clearer guidance when things go wrong
- **Improved reliability**: Retry logic prevents transient failures
- **Developer confidence**: Tests catch regressions

**User Value**: ⭐⭐⭐ (Behind-the-scenes improvement)
**Effort**: 🔨🔨🔨🔨 (4-6 hours)
**Dependencies**: None

#### What Needs to Be Done

1. **Add diagnostics.py** - Export config and coordinator status
2. **Improve error handling** - Retry logic, rate limit detection
3. **Add unit tests** - Test coordinator, sensor, config flow
4. **Add integration tests** - Test full setup flow
5. **Improve logging** - More context in error messages

#### Implementation Approach

**File: `custom_components/serac/diagnostics.py`** (NEW)
```python
"""Diagnostics support for Serac."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_BRA_TOKEN

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]

    # Redact sensitive data
    config_data = {**entry.data}
    if CONF_BRA_TOKEN in config_data:
        config_data[CONF_BRA_TOKEN] = "***REDACTED***"

    diagnostics_data = {
        "config_entry": config_data,
        "coordinators": {
            "arome": {
                "last_update_success": data["arome_coordinator"].last_update_success,
                "last_update": data["arome_coordinator"].last_update_success_time,
                "update_interval": str(data["arome_coordinator"].update_interval),
            }
        },
    }

    # Add BRA coordinator status
    if "bra_coordinators" in data:
        diagnostics_data["coordinators"]["bra"] = {}
        for massif_id, coordinator in data["bra_coordinators"].items():
            diagnostics_data["coordinators"]["bra"][str(massif_id)] = {
                "massif_name": coordinator.massif_name,
                "last_update_success": coordinator.last_update_success,
                "last_update": coordinator.last_update_success_time,
                "has_data": coordinator.data.get("has_data", False) if coordinator.data else False,
            }

    return diagnostics_data
```

**Enhanced Error Handling (coordinator.py):**
```python
# Add retry logic with exponential backoff
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import asyncio

async def _async_update_data_with_retry(self) -> dict[str, Any]:
    """Fetch data with retry logic."""
    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            return await self._async_update_data()
        except UpdateFailed as err:
            if attempt < max_retries - 1:
                _LOGGER.warning(
                    "Update failed (attempt %d/%d), retrying in %ds: %s",
                    attempt + 1,
                    max_retries,
                    retry_delay,
                    err,
                )
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise
```

**Unit Tests (tests/test_coordinator.py):** (NEW)
```python
"""Test Serac coordinators."""
import pytest
from unittest.mock import AsyncMock, patch

from custom_components.serac.coordinator import AromeCoordinator, BraCoordinator

async def test_arome_coordinator_success(hass):
    """Test AromeCoordinator successful update."""
    mock_client = AsyncMock()
    mock_client.async_get_current_weather.return_value = {"temperature": 20}
    mock_client.async_get_daily_forecast.return_value = [{"date": "2026-02-11"}]

    coordinator = AromeCoordinator(hass, mock_client, "Test Location")
    await coordinator.async_refresh()

    assert coordinator.data["current"]["temperature"] == 20
    assert len(coordinator.data["daily_forecast"]) == 1
```

#### Testing Plan

1. **Add diagnostics.py** and verify in Settings → Devices → Serac → Download Diagnostics
2. **Add retry logic** and test with simulated API failures
3. **Write unit tests** for coordinators, sensors, config flow
4. **Run tests** with `pytest tests/`
5. **Add GitHub Actions workflow** to run tests on PR

#### Estimated Effort
- Diagnostics: 1 hour
- Error handling improvements: 2 hours
- Unit tests: 2-3 hours
- Integration tests: 1 hour
- **Total: 4-6 hours**

---

## Implementation Order Recommendation

### ✅ Phase 1 (COMPLETE - v1.2.x)
1. **Options Flow** (2-3 hours) - ✅ Released in v1.2.0-v1.2.6
2. **Logo & Branding** (1-2 hours) - ✅ Released in v1.3.0

**Outcome**: Users can modify configuration, Serac has visual identity

### Phase 2 (Current - v1.4.0 target)
3. **Enhanced Documentation** (3-4 hours) - Screenshots, FAQ, French translation
4. **Diagnostics** (1 hour) - Easier issue debugging

**Expected outcome**: Better onboarding, easier troubleshooting

### Phase 3 (Near-term - v1.5.0 target)
5. **Weather Alerts (Vigilance)** (3-4 hours) - Mountain safety feature
6. **Code Quality** (3-5 hours) - Tests, error handling, logging

**Expected outcome**: Comprehensive mountain safety data, robust codebase

### Phase 4 (Long-term - v2.0.0+)
7. **Advanced Features** (variable) - Based on user feedback

**Expected outcome**: Mature, feature-rich integration

---

### Priority 5: Weather Alerts (Vigilance) ⚠️ (MOUNTAIN SAFETY)

**Why This Matters:**
- **Mountain safety critical**: Storm warnings, high wind alerts, snow/ice warnings
- **Natural complement**: Fits perfectly with weather + avalanche data
- **Same API ecosystem**: Uses Météo-France (like BRA), same token workflow
- **User expectation**: Mountain users need severe weather alerts
- **Competitive advantage**: HA's meteo_france integration uses city search, Serac can use GPS coordinates

**User Value**: ⭐⭐⭐⭐ (High safety value for mountain users)
**Effort**: 🔨🔨🔨 (3-4 hours)
**Dependencies**: Priority 3 (Documentation) should be done first

#### What Needs to Be Done

1. **Add Vigilance API client** - New vigilance_client.py for Météo-France alerts
2. **Create Vigilance coordinator** - 6-hour update interval (same as BRA)
3. **Add alert sensors** - Overall level + individual phenomenon types
4. **Update config flow** - Mention vigilance feature alongside BRA
5. **Update documentation** - Explain color codes and alert types

#### Weather Alert System Overview

**Météo-France Vigilance** provides department-level weather alerts with:
- **Color codes**: Green (safe), Yellow (watch), Orange (warning), Red (extreme danger)
- **Phenomena types**: Wind, rain-flood, thunderstorms, snow/ice, avalanche risk, extreme heat/cold, fog
- **Coverage**: All French departments + Andorra
- **Updates**: Real-time + 24-hour evolution timeline

#### Implementation Approach

**File: `custom_components/serac/api/vigilance_client.py`** (NEW)
```python
"""Météo-France Vigilance API client for weather alerts."""
from __future__ import annotations

import logging
from typing import Any
import aiohttp

_LOGGER = logging.getLogger(__name__)

# Department code lookup based on GPS coordinates
DEPARTMENT_BOUNDARIES = {
    # Alps departments (examples)
    "01": {"name": "Ain", "bounds": (45.0, 47.0, 4.7, 5.9)},
    "74": {"name": "Haute-Savoie", "bounds": (45.7, 46.4, 5.8, 7.0)},
    "73": {"name": "Savoie", "bounds": (45.0, 45.8, 5.6, 7.2)},
    # Add all French departments...
}

# Vigilance color codes
COLOR_CODES = {
    1: "green",      # Vert - No danger
    2: "yellow",     # Jaune - Be attentive
    3: "orange",     # Orange - Be very vigilant
    4: "red",        # Rouge - Absolute vigilance
}

# Phenomenon types
PHENOMENON_TYPES = {
    1: "wind",
    2: "rain_flood",
    3: "thunderstorm",
    4: "flood",
    5: "snow_ice",
    6: "extreme_heat",
    7: "extreme_cold",
    8: "avalanche",
    9: "fog",
}


class VigilanceApiError(Exception):
    """Exception raised for Vigilance API errors."""


class VigilanceClient:
    """Client for Météo-France Vigilance API."""

    def __init__(self, api_token: str, latitude: float, longitude: float) -> None:
        """Initialize the Vigilance client.

        Args:
            api_token: Météo-France API token (same as BRA)
            latitude: Location latitude
            longitude: Location longitude
        """
        self._api_token = api_token
        self._latitude = latitude
        self._longitude = longitude
        self._base_url = "https://public-api.meteofrance.fr/public/DPVigilance/v1"
        self._department = self._get_department_code(latitude, longitude)

    def _get_department_code(self, lat: float, lon: float) -> str:
        """Get department code from coordinates.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Two-digit department code (e.g., "74" for Haute-Savoie)
        """
        # Find department by checking coordinate bounds
        for dept_code, dept_info in DEPARTMENT_BOUNDARIES.items():
            bounds = dept_info["bounds"]
            if bounds[0] <= lat <= bounds[1] and bounds[2] <= lon <= bounds[3]:
                return dept_code

        # Fallback: use rough estimation
        # This is simplified - real implementation should use proper geographic lookup
        if 45.7 <= lat <= 46.4 and 5.8 <= lon <= 7.0:
            return "74"  # Haute-Savoie
        elif 45.0 <= lat <= 45.8 and 5.6 <= lon <= 7.2:
            return "73"  # Savoie

        return "74"  # Default to Haute-Savoie for Alps

    async def async_get_current_vigilance(self) -> dict[str, Any]:
        """Get current vigilance alerts for the department.

        Returns:
            Dictionary with vigilance data
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"apikey": self._api_token}
                url = f"{self._base_url}/cartevigilance/encours"

                async with session.get(
                    url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Extract data for our department
                    department_data = self._extract_department_data(data, self._department)

                    return {
                        "department": self._department,
                        "department_name": DEPARTMENT_BOUNDARIES.get(
                            self._department, {}
                        ).get("name", "Unknown"),
                        "overall_level": department_data.get("overall_level", 1),
                        "overall_color": COLOR_CODES.get(department_data.get("overall_level", 1)),
                        "phenomena": department_data.get("phenomena", {}),
                        "update_time": data.get("update_time"),
                        "has_data": True,
                    }

        except aiohttp.ClientResponseError as err:
            if err.status == 404:
                _LOGGER.warning("No vigilance data available for department %s", self._department)
                return {"has_data": False, "department": self._department}
            _LOGGER.error("HTTP error getting vigilance: %s", err, exc_info=True)
            raise VigilanceApiError(f"HTTP error: {err}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error getting vigilance: %s", err, exc_info=True)
            raise VigilanceApiError(f"Network error: {err}") from err
        except Exception as err:
            _LOGGER.error("Error getting vigilance: %s", err, exc_info=True)
            raise VigilanceApiError(f"Failed to get vigilance: {err}") from err

    def _extract_department_data(self, data: dict, dept_code: str) -> dict:
        """Extract vigilance data for specific department from API response.

        Args:
            data: Full API response
            dept_code: Department code (e.g., "74")

        Returns:
            Department-specific vigilance data
        """
        # Parse API response structure (simplified - adjust to actual API format)
        # Real implementation depends on actual Météo-France API response structure
        departments = data.get("zones", {})
        dept_data = departments.get(dept_code, {})

        return {
            "overall_level": dept_data.get("niveau_vigilance", 1),
            "phenomena": {
                phenom_type: {
                    "level": phenom_data.get("niveau", 1),
                    "color": COLOR_CODES.get(phenom_data.get("niveau", 1)),
                }
                for phenom_type, phenom_data in dept_data.get("phenomenes", {}).items()
            },
        }
```

**File: `custom_components/serac/coordinator.py`** (UPDATE)
```python
# Add new VigilanceCoordinator class

class VigilanceCoordinator(DataUpdateCoordinator):
    """Coordinator for Météo-France Vigilance data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: VigilanceClient,
        location_name: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Serac Vigilance ({location_name})",
            update_interval=timedelta(hours=6),  # Same as BRA
        )
        self._client = client
        self.location_name = location_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch vigilance data."""
        try:
            return await self._client.async_get_current_vigilance()
        except VigilanceApiError as err:
            raise UpdateFailed(f"Error fetching vigilance data: {err}") from err
```

**File: `custom_components/serac/sensor.py`** (UPDATE)
```python
# Add VigilanceSensor class

class VigilanceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Météo-France Vigilance alerts."""

    def __init__(
        self,
        coordinator: VigilanceCoordinator,
        entity_prefix: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entity_prefix = entity_prefix
        self._sensor_type = sensor_type
        self._attr_has_entity_name = False

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"serac_{self.coordinator._client._latitude}_{self.coordinator._client._longitude}_vigilance_{self._sensor_type}"

    @property
    def entity_id(self) -> str:
        """Return entity ID."""
        return f"sensor.serac_{self._entity_prefix}_vigilance_{self._sensor_type}"

    @property
    def name(self) -> str:
        """Return name."""
        if self._sensor_type == "level":
            return f"Serac {self._entity_prefix.title()} Vigilance Level"
        else:
            return f"Serac {self._entity_prefix.title()} Vigilance {self._sensor_type.replace('_', ' ').title()}"

    @property
    def native_value(self):
        """Return sensor value."""
        if not self.coordinator.data.get("has_data"):
            return None

        if self._sensor_type == "level":
            return self.coordinator.data.get("overall_level")
        elif self._sensor_type == "color":
            return self.coordinator.data.get("overall_color")
        else:
            # Individual phenomenon (wind, rain_flood, etc.)
            phenomena = self.coordinator.data.get("phenomena", {})
            phenom_data = phenomena.get(self._sensor_type, {})
            return phenom_data.get("level")

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if not self.coordinator.data.get("has_data"):
            return {}

        return {
            "department": self.coordinator.data.get("department"),
            "department_name": self.coordinator.data.get("department_name"),
            "update_time": self.coordinator.data.get("update_time"),
            "phenomena": self.coordinator.data.get("phenomena", {}),
        }
```

**File: `custom_components/serac/__init__.py`** (UPDATE)
```python
# In async_setup_entry, after BRA coordinators:

    # Set up Vigilance coordinator if BRA token provided
    vigilance_coordinator = None
    if bra_token:
        vigilance_client = VigilanceClient(bra_token, latitude, longitude)
        vigilance_coordinator = VigilanceCoordinator(hass, vigilance_client, location_name)
        await vigilance_coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id]["vigilance_coordinator"] = vigilance_coordinator
```

#### Sensor Design

**Sensors to create (when BRA token provided):**
1. **Overall vigilance level** - `sensor.serac_{prefix}_vigilance_level`
   - Value: 1-4 (Green/Yellow/Orange/Red)
   - State class: measurement

2. **Individual phenomena sensors** (optional - could be attributes instead):
   - `sensor.serac_{prefix}_vigilance_wind`
   - `sensor.serac_{prefix}_vigilance_rain_flood`
   - `sensor.serac_{prefix}_vigilance_thunderstorm`
   - `sensor.serac_{prefix}_vigilance_snow_ice`
   - Each shows level 1-4 for that phenomenon type

**Alternative simpler approach:** Just one sensor with all phenomena in attributes (like HA's meteo_france integration).

#### Testing Plan

1. **Get BRA API token** - Should work for both BRA and Vigilance endpoints
2. **Test department detection** - Verify GPS → department code mapping works
3. **Create vigilance coordinator** - Verify 6-hour update cycle
4. **Check sensor values** - Verify level, color, phenomena attributes
5. **Test without token** - Verify vigilance disabled when no BRA token
6. **Test outside France** - Verify graceful handling for non-French coordinates

#### Documentation Updates

**README.md additions:**
```markdown
### ⚠️ Weather Alerts (Vigilance)

When you provide a Météo-France BRA API token, Serac also fetches weather alerts (Vigilance) for your location:

- **Overall vigilance level** (1-4 scale: Green, Yellow, Orange, Red)
- **Individual alerts**: Wind, rain/flood, thunderstorms, snow/ice, fog, extreme temperatures
- **Department-based**: Alerts cover the French department your coordinates fall within
- **Update frequency**: Every 6 hours

**Example sensors:**
```yaml
sensor.serac_chamonix_vigilance_level  # 2 (Yellow)
# Attributes include:
# - department: "74" (Haute-Savoie)
# - phenomena: {wind: {level: 2, color: yellow}, snow_ice: {level: 1, color: green}}
```

**Use in automations:**
```yaml
automation:
  - alias: "High Wind Vigilance Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.serac_chamonix_vigilance_level
        above: 2  # Orange or Red
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Weather Alert"
          message: "Vigilance {{ states('sensor.serac_chamonix_vigilance_level') }} in effect!"
```
```

#### Estimated Effort
- API client implementation: 1.5 hours
- Coordinator setup: 30 minutes
- Sensor implementation: 1 hour
- Testing: 1 hour
- Documentation: 30 minutes
- **Total: 3-4 hours**

#### Future Enhancements
- **Map department boundaries properly** - Use shapefile or API for accurate GPS → department
- **Bulletin text** - Fetch full text descriptions of alerts
- **24-hour evolution** - Show how alerts will change over next day
- **Alert history** - Track when alerts were issued/lifted

---

## Nice-to-Have Features (Future Backlog)

### Advanced Data Features
- **Hourly avalanche risk evolution** - Show risk changes throughout the day
- **Snow depth sensors** - If API data becomes available
- **Historical data tracking** - Track conditions over time

### UX Enhancements
- **Custom update intervals** - Let users choose refresh rate
- **Location suggestions** - Auto-suggest based on nearby massifs
- **Dashboard card** - Custom Lovelace card for avalanche risk

### Multi-language Support
- **German UI** - For Swiss/Austrian Alps users
- **Italian UI** - For Italian Alps users
- **Spanish UI** - For Pyrenees users

---

## Success Metrics

### ✅ v1.2.0 Goals (Options Flow + Logo) - COMPLETE
- [x] Users can change massifs without reinstalling ✅
- [x] BRA token can be added/removed via UI ✅
- [x] Serac has custom logo in HA and HACS ✅
- [x] No breaking changes ✅
- [x] Zero GitHub issues about "can't change massifs" ✅

### v1.4.0 Goals (Documentation + Diagnostics)
- [ ] README has screenshots for all config steps
- [ ] FAQ section answers top 5 user questions
- [ ] French translation available
- [ ] Diagnostics data includes coordinator status
- [ ] Average issue resolution time < 24 hours

### v1.5.0 Goals (Weather Alerts + Code Quality)
- [ ] Weather alerts (Vigilance) for French departments
- [ ] Overall vigilance level sensor working
- [ ] Individual phenomenon alerts in attributes
- [ ] Unit test coverage > 50%
- [ ] Error retry logic in place
- [ ] Enhanced logging for debugging

### v2.0.0 Goals (Advanced Features)
- [ ] Unit test coverage > 70%
- [ ] Integration tests for all platforms
- [ ] At least 2 advanced features shipped (hourly risk, snow depth, etc.)
- [ ] Multi-language support (German, Italian)
- [ ] Custom Lovelace card (optional)

---

## Critical Files Reference

### For Options Flow
- `custom_components/serac/config_flow.py` - Add OptionsFlowHandler
- `custom_components/serac/__init__.py` - Reload logic (already exists)
- `custom_components/serac/strings.json` - Add options strings

### For Logo & Branding
- `custom_components/serac/icon.png` - New 256×256 logo
- `README.md` - Add logo to header
- `hacs.json` - Verify metadata

### For Documentation
- `README.md` - Add screenshots, FAQ, troubleshooting
- `docs/screenshots/` - New folder for images
- `custom_components/serac/translations/fr.json` - New French translation
- `CONTRIBUTING.md` - New developer guide

### For Diagnostics & Quality
- `custom_components/serac/diagnostics.py` - New diagnostics support
- `custom_components/serac/coordinator.py` - Enhanced error handling
- `tests/test_coordinator.py` - New unit tests
- `tests/test_config_flow.py` - New config flow tests
- `.github/workflows/test.yml` - New CI workflow

---

## Risk Assessment

### Low Risk
- ✅ Options Flow - Uses existing reload pattern, no entity ID changes
- ✅ Logo - Static asset, no code impact
- ✅ Documentation - External to code

### Medium Risk
- ⚠️ Diagnostics - New file, must redact sensitive data
- ⚠️ Error handling - Could mask real issues if not careful

### High Risk
- ❌ Breaking entity ID changes - AVOID (unless v2.0.0 major release)
- ❌ Domain changes - AVOID (just did this in v1.0.0)

---

## Next Actions

1. ✅ ~~**Options Flow**~~ - COMPLETE (v1.2.0-v1.2.6)
2. ✅ ~~**Logo & Branding**~~ - COMPLETE (v1.3.0)
3. 🔄 **Enhanced Documentation** (Priority 3) - **NEXT** (3-4 hours)
   - Take screenshots of config flow
   - Add FAQ section
   - Create French translation
4. 📋 **Diagnostics** (Priority 4) - After documentation (1 hour)
5. ⚠️ **Weather Alerts** (Priority 5) - New mountain safety feature (3-4 hours)
6. 🔧 **Code Quality** (Priority 4 continued) - Tests, error handling (3-5 hours)

---

**Current Status**: v1.3.0 released (Logo & Branding complete)
**Recommended Next Task**: Enhanced Documentation (Priority 3)
**Estimated Time to v1.4.0 Release**: 1-2 weeks (Documentation + Diagnostics)
**Estimated Time to v1.5.0 Release**: 3-4 weeks (Weather Alerts + Code Quality)
