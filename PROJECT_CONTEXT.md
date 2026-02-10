# Project Context - A Better Mountain Weather

## Project Overview

**Domain**: `better_mountain_weather`
**Repository**: https://github.com/atacamalabs/ha-better-mountain-weather
**Current Version**: v0.1.0b1 (Beta 1)
**Status**: Phase 1 Complete ✅ | Phase 2 Ready to Start | Phase 3 Planned

This is a Home Assistant HACS integration providing comprehensive mountain weather data for French Alps, Pyrenees, and Corsica by combining two Météo-France APIs:
1. **AROME API** - Weather forecasts (JSON, via meteofrance-api library)
2. **BRA API** - Avalanche risk bulletins (XML, custom client needed)

## Current Implementation Status

### ✅ Phase 1: AROME Weather Integration (COMPLETE)

**Version**: v0.1.0b1
**Released**: 2026-02-10
**GitHub**: https://github.com/atacamalabs/ha-better-mountain-weather/releases/tag/v0.1.0b1

#### What's Implemented:

**Core Files:**
- ✅ `manifest.json` - Domain, version, dependencies (meteofrance-api>=1.5.0, lxml>=5.0.0)
- ✅ `const.py` - All 40 French massifs mapped with coordinates, sensor types defined
- ✅ `config_flow.py` - Two-step config: API tokens → GPS coordinates with validation
- ✅ `__init__.py` - Integration setup with AROME coordinator initialization
- ✅ `coordinator.py` - AromeCoordinator (1h updates) + BraCoordinator stub (Phase 2)
- ✅ `strings.json` + `translations/en.json` - Config flow UI text
- ✅ `api/arome_client.py` - Wrapper for meteofrance-api library
- ✅ `weather.py` - Weather entity with daily/hourly forecasts
- ✅ `sensor.py` - 11 AROME sensors implemented

**Repository Files:**
- ✅ `README.md` - Complete user documentation
- ✅ `hacs.json` - HACS metadata
- ✅ `LICENSE` - MIT
- ✅ `.gitignore` - Python/HA standard
- ✅ `.github/workflows/validate.yml` - CI validation

**Features Working:**
- Weather entity with current conditions
- 7-day daily forecast + 48-hour hourly forecast
- 11 AROME sensors: elevation, UV index, sunrise/sunset, cloud coverage, humidity, wind speed/gusts (current and today max)
- GPS-based location setup
- Automatic massif detection (saved in config for Phase 2)

**Known Limitations:**
- Sunrise/sunset: Using simplified calculation (should improve with astral library)
- Air quality: Not provided by meteofrance-api (sensor shows None)
- BRA sensors: Stub only, Phase 2 implementation needed

### 🔄 Phase 2: BRA Avalanche Integration (READY TO START)

**Target Version**: v0.2.0b1
**Estimated Complexity**: Medium (3-4 hours)

#### What Needs to Be Implemented:

**1. BRA API Client** (`api/bra_client.py` - NEW FILE)
- XML parser using `lxml.etree`
- Authentication: BRA token in headers (`apikey: token`)
- Endpoint: `https://public-api.meteofrance.fr/public/DPBRA/v1`
- Methods needed:
  - `async def authenticate()` - Validate BRA token
  - `async def get_bulletin(massif_id)` - Fetch BRA XML for massif
  - `def parse_bulletin_xml(xml_string)` - Parse to structured dict
- Reference implementation: https://github.com/cnico/ha-meteofrance-montagne (api.py)

**2. BRA Coordinator** (UPDATE `coordinator.py`)
- Complete the `BraCoordinator` class (currently stub)
- 6-hour update interval (bulletins published daily, check frequently)
- Initialize with BRA client and massif_id
- Parse XML response to extract:
  - Risk level (1-5) by altitude zone
  - Risk trend (stable/increasing/decreasing)
  - Snowpack quality description
  - Recent snowfall (cm)
  - Altitude limits
  - Wind transport risk
  - Wet snow risk
  - Accidental trigger risk
- Graceful error handling if no bulletin available

**3. BRA Sensors** (UPDATE `sensor.py`)
Add 8 new sensor descriptions to AROME_SENSORS tuple:
- `SENSOR_TYPE_AVALANCHE_RISK` - State 1-5, attributes: text, color, commentary
- `SENSOR_TYPE_RISK_TREND` - stable/increasing/decreasing
- `SENSOR_TYPE_SNOWPACK_QUALITY` - Text description
- `SENSOR_TYPE_RECENT_SNOW` - cm (SensorDeviceClass.PRECIPITATION)
- `SENSOR_TYPE_RISK_ALTITUDE_HIGH` - meters (SensorDeviceClass.DISTANCE)
- `SENSOR_TYPE_RISK_ALTITUDE_LOW` - meters (SensorDeviceClass.DISTANCE)
- `SENSOR_TYPE_WIND_TRANSPORT_RISK` - 1-5 scale
- `SENSOR_TYPE_WET_SNOW_RISK` - 1-5 scale

**4. Config Flow Enhancement** (UPDATE `config_flow.py`)
- After location step, add new `async_step_massif()` step
- Display auto-detected massif with option to override
- Provide dropdown with all 40 massifs grouped by region:
  - Alps (23): CHABLAIS, ARAVIS, MONT-BLANC, etc.
  - Pyrenees (16): PAYS-BASQUE, ASPE-OSSAU, etc.
  - Corsica (1): CORSE
- Store selected massif_id and massif_name in config entry

**5. Integration Setup** (UPDATE `__init__.py`)
- Uncomment BRA coordinator initialization section
- Initialize BRA client with token and massif_id
- Create BraCoordinator
- Fetch initial data (with error handling)
- Store in hass.data[DOMAIN][entry.entry_id]["bra_coordinator"]
- Ensure AROME continues working even if BRA fails

**6. Update manifest.json**
- Change version to "0.2.0b1"

#### Testing Checklist for Phase 2:
- [ ] BRA token validates correctly
- [ ] Massif auto-detection works for test locations
- [ ] Manual massif override functions
- [ ] 8 BRA sensors appear with valid data
- [ ] BRA updates every 6 hours
- [ ] Avalanche risk matches official Météo-France website
- [ ] BRA failure doesn't break AROME functionality
- [ ] Test with location outside France (should handle gracefully)

#### Release Process:
```bash
# After implementing and testing
git add .
git commit -m "Add BRA avalanche risk integration (Phase 2)

- Implement BRA API client with XML parsing
- Add BRA coordinator with 6-hour updates
- Create 8 avalanche risk sensors
- Add massif selection step to config flow
- Update integration to initialize both coordinators

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
"
git tag -a v0.2.0b2 -m "Beta 2: BRA avalanche risk sensors"
git push origin main
git push origin v0.2.0b1

# Then create GitHub release (mark as pre-release)
gh release create v0.2.0b1 --prerelease --title "v0.2.0b1 - Beta 2: BRA Avalanche Data" --notes "..."
```

### 📋 Phase 3: Polish & Stable Release (PLANNED)

**Target Version**: v1.0.0
**Status**: After Phase 2 testing complete

#### What Needs to Be Implemented:

**1. Diagnostics Support** (NEW FILE: `diagnostics.py`)
```python
async def async_get_config_entry_diagnostics(hass, entry):
    """Return diagnostics for a config entry."""
    # Redact API tokens
    # Include configuration dump
    # Sample API responses (redacted)
    # Coordinator update statistics
    # Last successful update timestamps
    # Error history
```

**2. Error Handling Improvements**
- Retry logic with exponential backoff
- Better network timeout handling
- User-friendly error messages in logs
- Detect rate limiting and adjust accordingly

**3. Sunrise/Sunset Improvement**
- Replace simplified calculation in `arome_client.py`
- Use `astral` library for accurate calculations
- Add to requirements in manifest.json

**4. Code Quality**
- Add type hints throughout (currently partial)
- Complete docstrings for all public methods
- Run validation: black, flake8, mypy
- Add pre-commit hooks

**5. Documentation**
- Add screenshots to README
- French translation (translations/fr.json)
- Contributing guidelines
- API token acquisition screenshots

**6. Testing**
- Unit tests for API clients
- Integration tests for coordinators
- Mock API responses for tests

#### Release as v1.0.0:
```bash
git add .
git commit -m "Stable release: v1.0.0"
git tag -a v1.0.0 -m "Stable release: AROME + BRA integration"
git push origin main
git push origin v1.0.0
gh release create v1.0.0 --title "v1.0.0 - Stable Release" --notes "..."
# Do NOT mark as pre-release
```

## Key Technical Details

### API Endpoints

**AROME (via meteofrance-api library):**
- Library handles all API calls
- Base URL: Managed by library
- Authentication: API key in library initialization
- Rate limits: Managed by library
- Response format: Python objects

**BRA (custom client needed):**
- Base URL: `https://public-api.meteofrance.fr/public/DPBRA/v1`
- Endpoint: `/bulletins/{massif_id}`
- Authentication: `apikey: {token}` in headers
- Response format: XML
- Update frequency: Daily bulletins, check every 6 hours

### Massif Detection Logic

Using haversine distance formula in `config_flow.py`:
```python
def _find_nearest_massif(latitude: float, longitude: float) -> tuple[str, str]:
    # Calculate distance from GPS to each massif centroid
    # Return (massif_id, massif_name) of nearest
```

All 40 massifs defined in `const.py` with approximate centroids.

### Data Flow

1. **Config Flow**: User enters tokens + GPS → Validates → Detects massif → Creates config entry
2. **Setup**: `__init__.py` initializes clients and coordinators
3. **Updates**:
   - AROME: Every 1 hour, fetches weather data
   - BRA: Every 6 hours, fetches avalanche bulletin
4. **Entities**: Weather entity + sensors pull from coordinator.data

### Error Handling Strategy

- AROME failure: Raise ConfigEntryNotReady, retry later
- BRA failure: Log error but allow AROME to continue (graceful degradation)
- Invalid coordinates: Show error in config flow
- Rate limiting: Respect API quotas, exponential backoff

## User Information

**GitHub Account**: atacamalabs
**Email**: hi@atacamalabs.com
**Git User**: atacamalabs

**API Tokens Needed for Testing:**
- AROME: From https://portail-api.meteofrance.fr/
- BRA: From same portal

**Test Locations:**
- Chamonix (Mont-Blanc): 45.9237, 6.8694
- Grenoble (Chartreuse): 45.1885, 5.7245
- Val d'Isère (Haute-Tarentaise): 45.4486, 6.9808

## File Locations

**Project Root**: `/Users/g/claude/abetterweather/`

**Integration Files**: `/Users/g/claude/abetterweather/custom_components/better_mountain_weather/`

**Key Files to Modify for Phase 2:**
- `api/bra_client.py` - CREATE NEW
- `coordinator.py` - COMPLETE BraCoordinator class
- `sensor.py` - ADD 8 BRA sensors
- `config_flow.py` - ADD massif selection step
- `__init__.py` - UNCOMMENT BRA initialization
- `manifest.json` - UPDATE version to 0.2.0b1

## References

**Similar Implementations:**
- https://github.com/cnico/ha-meteofrance-montagne - BRA API patterns
- https://github.com/hacf-fr/meteofrance-api - AROME library

**Home Assistant:**
- Developer Docs: https://developers.home-assistant.io/
- Weather Entity: https://developers.home-assistant.io/docs/core/entity/weather/
- Sensor Entity: https://developers.home-assistant.io/docs/core/entity/sensor/
- Config Flow: https://developers.home-assistant.io/docs/config_entries_config_flow_handler/

**HACS:**
- Documentation: https://hacs.xyz/
- Integration Requirements: https://hacs.xyz/docs/publish/integration

## Quick Commands

```bash
# Navigate to project
cd /Users/g/claude/abetterweather

# Check status
git status
git log --oneline

# Test Python syntax
python3 -m py_compile custom_components/better_mountain_weather/*.py

# Push changes
git add .
git commit -m "Message"
git push origin main

# Create tag and release
git tag -a vX.Y.Z -m "Message"
git push origin vX.Y.Z
gh release create vX.Y.Z --prerelease --title "Title" --notes "Notes"

# Test in Home Assistant
# 1. Add custom repo in HACS: https://github.com/atacamalabs/ha-better-mountain-weather
# 2. Install integration
# 3. Restart HA
# 4. Add integration via UI
```

## Important Notes for Next Session

1. **Phase 1 is complete and tested** - Don't redo AROME implementation
2. **BRA coordinator stub exists** - Just needs completion, not creation
3. **Massif detection works** - Already saves massif_id/name to config
4. **All 40 massifs mapped** - In const.py with coordinates
5. **Config flow is two-step** - Don't add massif step until Phase 2
6. **Version numbering**: 0.1.0b1 (current) → 0.2.0b1 (Phase 2) → 1.0.0 (stable)
7. **GitHub is live** - Don't recreate repo, just push updates
8. **Authentication configured** - atacamalabs account active

## Questions for User Before Starting Phase 2

- [ ] Has Phase 1 been tested in Home Assistant?
- [ ] Do you have access to BRA API token?
- [ ] Any issues found in Phase 1 that need fixing first?
- [ ] Any changes to Phase 2 requirements?

---

**Last Updated**: 2026-02-10 by Claude Sonnet 4.5
**Next Step**: User testing Phase 1, then implement Phase 2
