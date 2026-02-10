# Original Implementation Plan

This is the complete implementation plan that was followed for Phase 1 and will guide Phase 2 and 3.

## Project Goal

Create a Home Assistant HACS integration called "A Better Mountain Weather" that provides comprehensive mountain weather data for French Alps, Pyrenees, and Corsica by combining:
1. AROME API (Météo-France) - Weather forecasts
2. BRA API (Météo-France) - Avalanche risk bulletins

## Phased Approach

### Phase 1: Foundation + AROME API ✅ COMPLETE
Build core integration with weather forecasts first. This provides immediate value and establishes the foundation.

**Deliverable**: v0.1.0b1 - Working weather integration
**Status**: Released 2026-02-10

### Phase 2: Add BRA Avalanche Data 🔄 NEXT
Extend with avalanche risk sensors using custom XML client.

**Deliverable**: v0.2.0b1 - Weather + Avalanche data
**Status**: Ready to implement

### Phase 3: Polish for Stable Release 📋 PLANNED
Improve error handling, add diagnostics, enhance documentation.

**Deliverable**: v1.0.0 - Production ready
**Status**: After Phase 2 testing

## Architecture Design

### Single Integration with Dual Coordinators

**Domain**: `better_mountain_weather`

**Config Entry Design:**
- Single config entry stores:
  - Both API tokens (AROME + BRA)
  - GPS coordinates (latitude, longitude)
  - Location name (from AROME API)
  - Massif ID and name (auto-detected, user can override)

**Two DataUpdateCoordinator instances:**
1. **AromeCoordinator**: Updates every 1 hour
2. **BraCoordinator**: Updates every 6 hours

**Entity Organization:**
- 1 Weather entity: `weather.better_mountain_weather_{location}`
- 11 AROME sensors (Phase 1) ✅
- 8 BRA sensors (Phase 2) 🔄

**API Integration:**
- AROME: Use `meteofrance-api` Python library ✅
- BRA: Custom XML client using `lxml` 🔄

### User Experience

**Config Flow Steps:**
1. Enter AROME API token
2. Enter BRA API token
3. Enter GPS coordinates (validates location)
4. (Phase 2) Confirm or override auto-detected massif

**Why This Design:**
- Single config entry = simpler UX
- Dual coordinators = different update frequencies
- AROME first = quick value, simpler implementation
- BRA optional = graceful degradation if unavailable

## File Structure

```
/Users/g/claude/abetterweather/
├── .github/workflows/
│   └── validate.yml              # CI validation
├── custom_components/better_mountain_weather/
│   ├── __init__.py               # Integration setup
│   ├── manifest.json             # Metadata, version, dependencies
│   ├── const.py                  # Constants, massifs, sensors
│   ├── config_flow.py            # UI configuration
│   ├── coordinator.py            # Both coordinators
│   ├── weather.py                # Weather entity
│   ├── sensor.py                 # All sensors (AROME + BRA)
│   ├── diagnostics.py            # Phase 3
│   ├── strings.json              # Config flow text
│   ├── translations/en.json      # English translations
│   └── api/
│       ├── __init__.py
│       ├── arome_client.py       # AROME wrapper ✅
│       └── bra_client.py         # BRA XML parser 🔄
├── hacs.json                     # HACS metadata
├── README.md                     # User documentation
├── LICENSE                       # MIT
├── .gitignore                    # Python/HA excludes
├── DEVELOPMENT.md                # Phase 2/3 guide
├── QUICKSTART.md                 # Setup instructions
├── PROJECT_CONTEXT.md            # This file - session context
└── IMPLEMENTATION_PLAN.md        # Original plan
```

## Phase 1 Details (COMPLETE)

### Implementation Steps Completed:

1. ✅ Repository setup with HACS structure
2. ✅ manifest.json with dependencies
3. ✅ const.py with 40 massifs mapped
4. ✅ config_flow.py (two-step: tokens → GPS)
5. ✅ api/arome_client.py (meteofrance-api wrapper)
6. ✅ coordinator.py (AromeCoordinator + BraCoordinator stub)
7. ✅ weather.py (entity with forecasts)
8. ✅ sensor.py (11 AROME sensors)
9. ✅ __init__.py (integration setup)
10. ✅ strings.json + translations
11. ✅ hacs.json
12. ✅ README.md (comprehensive docs)
13. ✅ .github/workflows/validate.yml
14. ✅ Git repository initialized
15. ✅ Tagged as v0.1.0b1
16. ✅ Pushed to GitHub
17. ✅ GitHub Release created

### AROME Sensors (11 total):

1. Elevation - meters
2. Air Quality - AQI (returns None - not in API)
3. UV Index - 0-11
4. Sunrise - timestamp
5. Sunset - timestamp
6. Cloud Coverage - percentage
7. Humidity - percentage
8. Wind Speed (Current) - km/h
9. Wind Gust (Current) - km/h
10. Wind Speed Today Max - km/h
11. Wind Gust Today Max - km/h

### Weather Entity Features:

- Current conditions (temp, humidity, pressure, wind, clouds)
- 7-day daily forecast
- 48-hour hourly forecast
- UV index in state
- Elevation in attributes

## Phase 2 Details (READY TO START)

### Implementation Steps Required:

#### 1. Create BRA API Client

**File**: `custom_components/better_mountain_weather/api/bra_client.py` (NEW)

**Implementation Requirements:**
- Use `lxml.etree` for XML parsing
- Endpoint: `https://public-api.meteofrance.fr/public/DPBRA/v1`
- Authentication: Header `apikey: {token}`
- Methods needed:
  ```python
  async def authenticate() -> bool
  async def get_bulletin(massif_id: str) -> dict
  def parse_bulletin_xml(xml_string: str) -> dict
  ```

**Data to Extract from XML:**
- Risk level (1-5) by altitude
- Risk trend (stable/increasing/decreasing)
- Snowpack quality (text)
- Recent snowfall (cm, last 24h)
- Altitude limits (high/low risk zones)
- Wind transport risk (1-5)
- Wet snow risk (1-5)
- Accidental trigger risk (text)

**Reference Implementation:**
- https://github.com/cnico/ha-meteofrance-montagne/blob/main/custom_components/meteofrance_montagne/api.py

#### 2. Complete BRA Coordinator

**File**: `coordinator.py` (UPDATE)

**Current State**: Stub exists with 6-hour update interval

**Required Changes:**
- Initialize BRA client in `__init__`
- Implement `_async_update_data()`:
  - Call `client.get_bulletin(massif_id)`
  - Parse XML response
  - Return structured dict
  - Handle errors gracefully (no bulletin available, network errors)
- Store data in format matching sensor expectations

#### 3. Add BRA Sensors

**File**: `sensor.py` (UPDATE)

**Add 8 New Sensors:**

```python
BetterMountainWeatherSensorDescription(
    key=SENSOR_TYPE_AVALANCHE_RISK,
    name="Avalanche Risk",
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:avalanche",
    # State: 1-5
    # Attributes: risk_text, risk_color, commentary
),
BetterMountainWeatherSensorDescription(
    key=SENSOR_TYPE_RISK_TREND,
    name="Risk Trend",
    icon="mdi:trending-up",
    # State: stable/increasing/decreasing
),
BetterMountainWeatherSensorDescription(
    key=SENSOR_TYPE_SNOWPACK_QUALITY,
    name="Snowpack Quality",
    icon="mdi:snowflake",
    # State: text description
),
BetterMountainWeatherSensorDescription(
    key=SENSOR_TYPE_RECENT_SNOW,
    name="Recent Snow",
    native_unit_of_measurement=UnitOfLength.CENTIMETERS,
    device_class=SensorDeviceClass.PRECIPITATION,
    state_class=SensorStateClass.MEASUREMENT,
    # State: cm in last 24h
),
BetterMountainWeatherSensorDescription(
    key=SENSOR_TYPE_RISK_ALTITUDE_HIGH,
    name="Risk Altitude High",
    native_unit_of_measurement=UnitOfLength.METERS,
    device_class=SensorDeviceClass.DISTANCE,
    icon="mdi:elevation-rise",
    # State: meters
),
BetterMountainWeatherSensorDescription(
    key=SENSOR_TYPE_RISK_ALTITUDE_LOW,
    name="Risk Altitude Low",
    native_unit_of_measurement=UnitOfLength.METERS,
    device_class=SensorDeviceClass.DISTANCE,
    icon="mdi:elevation-decline",
    # State: meters
),
BetterMountainWeatherSensorDescription(
    key=SENSOR_TYPE_WIND_TRANSPORT_RISK,
    name="Wind Transport Risk",
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:weather-windy",
    # State: 1-5
),
BetterMountainWeatherSensorDescription(
    key=SENSOR_TYPE_WET_SNOW_RISK,
    name="Wet Snow Risk",
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:water-alert",
    # State: 1-5
),
```

**Update `async_setup_entry()`:**
- Check if BRA coordinator exists in hass.data
- If yes, create BRA sensors linked to BRA coordinator
- If no, only create AROME sensors (backward compatibility)

#### 4. Enhance Config Flow

**File**: `config_flow.py` (UPDATE)

**Add New Step After Location:**

```python
async def async_step_massif(
    self, user_input: dict[str, Any] | None = None
) -> FlowResult:
    """Handle massif selection step."""
    errors: dict[str, str] = {}

    if user_input is not None:
        # Store selected massif
        self._data[CONF_MASSIF_ID] = user_input[CONF_MASSIF_ID]
        self._data[CONF_MASSIF_NAME] = MASSIFS[user_input[CONF_MASSIF_ID]][0]

        # Create config entry
        await self.async_set_unique_id(...)
        return self.async_create_entry(...)

    # Get auto-detected massif
    detected_id = self._data[CONF_MASSIF_ID]
    detected_name = self._data[CONF_MASSIF_NAME]

    # Create dropdown with all massifs
    massif_options = {
        massif_id: f"{name} ({massif_id})"
        for massif_id, (name, _, _) in MASSIFS.items()
    }

    data_schema = vol.Schema({
        vol.Required(
            CONF_MASSIF_ID,
            default=detected_id
        ): vol.In(massif_options),
    })

    return self.async_show_form(
        step_id="massif",
        data_schema=data_schema,
        description_placeholders={
            "detected_massif": detected_name,
        },
    )
```

**Update `async_step_location()`:**
- After validating location, call `async_step_massif()` instead of creating entry

**Update strings.json:**
Add massif step text

#### 5. Update Integration Setup

**File**: `__init__.py` (UPDATE)

**Uncomment BRA Initialization:**

```python
# Initialize BRA coordinator if token provided
if bra_token and massif_id:
    try:
        bra_client = BraClient(
            api_key=bra_token,
            massif_id=massif_id,
            session=session,
        )

        bra_coordinator = BraCoordinator(
            hass=hass,
            client=bra_client,
            location_name=location_name,
            massif_id=massif_id,
        )

        await bra_coordinator.async_config_entry_first_refresh()

        hass.data[DOMAIN][entry.entry_id]["bra_coordinator"] = bra_coordinator
        hass.data[DOMAIN][entry.entry_id]["bra_client"] = bra_client

        _LOGGER.info("BRA coordinator initialized for massif %s", massif_id)
    except Exception as err:
        # Log but don't fail - AROME still works
        _LOGGER.warning("Failed to initialize BRA coordinator: %s", err)
```

#### 6. Update Version

**File**: `manifest.json` (UPDATE)

Change: `"version": "0.2.0b1"`

### Testing Phase 2:

**Before Release:**
- [ ] BRA client authenticates successfully
- [ ] BRA client fetches and parses XML bulletin
- [ ] 8 BRA sensors appear in HA
- [ ] BRA sensors show correct data
- [ ] Compare sensor data with official Météo-France website
- [ ] BRA coordinator updates every 6 hours
- [ ] AROME continues working if BRA fails
- [ ] Massif selection UI works
- [ ] Auto-detection picks correct massif
- [ ] Manual override changes massif correctly

**Test Scenarios:**
1. New installation with both tokens
2. Upgrade from v0.1.0b1
3. Invalid BRA token (should log error, AROME works)
4. Location outside France (no valid massif)
5. BRA API down (graceful degradation)

### Release Process Phase 2:

```bash
# After implementation and testing
git add .
git commit -m "Add BRA avalanche risk integration (Phase 2)"
git tag -a v0.2.0b1 -m "Beta 2: BRA avalanche risk sensors"
git push origin main
git push origin v0.2.0b1
gh release create v0.2.0b1 --prerelease --title "..." --notes "..."
```

## Phase 3 Details (PLANNED)

### Implementation Steps Required:

#### 1. Diagnostics Support

**File**: `diagnostics.py` (NEW)

```python
async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinators = hass.data[DOMAIN][entry.entry_id]

    diagnostics = {
        "config": {
            "latitude": entry.data[CONF_LATITUDE],
            "longitude": entry.data[CONF_LONGITUDE],
            "location_name": entry.data[CONF_LOCATION_NAME],
            "massif_id": entry.data.get(CONF_MASSIF_ID),
            "massif_name": entry.data.get(CONF_MASSIF_NAME),
            # Redact tokens
            "arome_token": "***REDACTED***",
            "bra_token": "***REDACTED***",
        },
        "arome_coordinator": {
            "last_update_success": coordinators["arome_coordinator"].last_update_success,
            "last_update": coordinators["arome_coordinator"].last_update_success_time,
            "update_interval": str(coordinators["arome_coordinator"].update_interval),
            "data_sample": {
                "elevation": coordinators["arome_coordinator"].data.get("elevation"),
                "current_temp": coordinators["arome_coordinator"].data.get("current", {}).get("temperature"),
                "forecast_count": len(coordinators["arome_coordinator"].data.get("daily_forecast", [])),
            },
        },
    }

    # Add BRA coordinator if exists
    if "bra_coordinator" in coordinators:
        diagnostics["bra_coordinator"] = {
            "last_update_success": coordinators["bra_coordinator"].last_update_success,
            "last_update": coordinators["bra_coordinator"].last_update_success_time,
            "update_interval": str(coordinators["bra_coordinator"].update_interval),
        }

    return diagnostics
```

#### 2. Improve Sunrise/Sunset

**File**: `api/arome_client.py` (UPDATE)

**Current Implementation**: Simplified calculation
**Target**: Use `astral` library

```python
from astral import LocationInfo
from astral.sun import sun

def get_sun_times(latitude: float, longitude: float, date: datetime) -> dict:
    """Calculate accurate sunrise/sunset times."""
    location = LocationInfo("", "", "UTC", latitude, longitude)
    s = sun(location.observer, date=date)
    return {
        "sunrise": s["sunrise"],
        "sunset": s["sunset"],
    }
```

**Update manifest.json**: Add `astral>=3.0` to requirements

#### 3. Code Quality Improvements

**Add Type Hints:**
- Review all files
- Add missing type hints
- Use `from typing import` for complex types

**Complete Docstrings:**
- All public methods need docstrings
- Format: Google style
- Include Args, Returns, Raises

**Run Linters:**
```bash
pip install black flake8 mypy
black custom_components/better_mountain_weather/
flake8 custom_components/better_mountain_weather/
mypy custom_components/better_mountain_weather/
```

**Pre-commit Hooks:**
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

#### 4. Enhanced Documentation

**README.md Updates:**
- Add screenshots of weather card
- Add screenshots of sensor cards
- Add screenshots of config flow
- Add troubleshooting section
- Add FAQ section

**Add French Translation:**
Create `translations/fr.json` with French UI text

**Contributing Guide:**
Create `CONTRIBUTING.md` with:
- How to set up dev environment
- How to run tests
- Code style requirements
- PR process

#### 5. Testing

**Unit Tests:**
Create `tests/` directory with:
- `test_arome_client.py` - Mock API responses
- `test_bra_client.py` - Mock XML parsing
- `test_config_flow.py` - Test validation
- `test_coordinators.py` - Test updates

**Integration Tests:**
- Test full setup flow
- Test entity creation
- Test data updates

#### 6. Error Handling Enhancements

**Retry Logic:**
- Implement exponential backoff for API failures
- Max retries: 3
- Backoff: 1s, 2s, 4s

**Rate Limiting:**
- Detect 429 responses
- Adjust update interval temporarily
- Log warnings

**Network Timeouts:**
- Increase timeout for BRA XML (large files)
- Add connection pool settings

### Release Process Phase 3:

```bash
# After all improvements
git add .
git commit -m "Stable release: v1.0.0"
git tag -a v1.0.0 -m "Stable release: Full AROME + BRA integration"
git push origin main
git push origin v1.0.0
gh release create v1.0.0 --title "v1.0.0 - Stable Release" --notes "..."
# NOT marked as pre-release
```

## Versioning Strategy

**Semantic Versioning**: MAJOR.MINOR.PATCH

**Beta Releases:**
- 0.1.0b1, 0.1.0b2, ... - AROME only
- 0.2.0b1, 0.2.0b2, ... - AROME + BRA

**Release Candidates:**
- 1.0.0rc1, 1.0.0rc2 - Feature complete, final testing

**Stable:**
- 1.0.0 - Initial stable release
- 1.0.x - Bug fixes only
- 1.x.0 - New features (minor)
- 2.0.0 - Breaking changes (major)

## Success Criteria

### Phase 1 (Complete):
- ✅ Integration installs via HACS
- ✅ Config flow accepts tokens and GPS
- ✅ Weather entity shows current conditions
- ✅ Daily and hourly forecasts available
- ✅ 11 AROME sensors populated
- ✅ Updates every hour
- ✅ No errors in logs

### Phase 2 (Target):
- [ ] 8 BRA sensors appear
- [ ] Avalanche risk data accurate
- [ ] Massif selection works
- [ ] BRA updates every 6 hours
- [ ] AROME continues if BRA fails
- [ ] Upgrade from v0.1.0b1 works smoothly

### Phase 3 (Target):
- [ ] Diagnostics available
- [ ] Code quality: 100% type hints, full docstrings
- [ ] All tests passing
- [ ] Documentation complete with screenshots
- [ ] Zero errors in validation
- [ ] Ready for HACS default repository

## Notes for Implementation

**Important Decisions Made:**
1. Single integration (not separate AROME/BRA integrations)
2. Both API tokens required (could make BRA optional in future)
3. Massif auto-detection with override (better UX than manual only)
4. Graceful BRA degradation (AROME continues if BRA fails)
5. 1h and 6h update intervals (based on API update frequencies)

**Things to Avoid:**
- Don't create separate integrations - keep as single integration
- Don't make massif selection mandatory - auto-detection should work for most
- Don't fail setup if BRA unavailable - AROME is still valuable
- Don't over-engineer - keep it simple and maintainable

**Future Enhancements (Post-v1.0.0):**
- Support for other countries (Switzerland, Italy, Austria)
- Weather alerts/warnings
- Historical data tracking
- Custom update intervals
- Multiple locations in single instance

---

**Document Version**: 1.0
**Last Updated**: 2026-02-10
**Status**: Phase 1 Complete, Phase 2 Ready
