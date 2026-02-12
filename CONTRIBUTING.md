# Contributing to Serac

Thank you for your interest in contributing to Serac! This guide will help you get started with development.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Adding New Features](#adding-new-features)

---

## Code of Conduct

Be respectful and constructive. We're all here to build something useful for the mountain community.

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Home Assistant development environment
- Git
- A Météo-France BRA API token (for testing avalanche features)

### Where to Contribute

- 🐛 **Bug fixes** - Always welcome!
- 📚 **Documentation** - Improve README, add examples, fix typos
- ✨ **New features** - Check [ROADMAP.md](ROADMAP.md) for planned features
- 🌍 **Translations** - Add support for more languages
- 🧪 **Tests** - Improve test coverage

---

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/ha-serac.git
cd ha-serac
```

### 2. Set Up Home Assistant Development Environment

**Option A: Use a test Home Assistant installation**
```bash
# Copy integration to your HA config folder
cp -r custom_components/serac /path/to/homeassistant/config/custom_components/

# Restart Home Assistant
```

**Option B: Use Home Assistant Core in a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install homeassistant
```

### 3. Install Development Dependencies

```bash
pip install -r requirements_dev.txt  # If it exists, otherwise:
pip install pytest pytest-homeassistant-custom-component
```

### 4. Test Your Setup

Add the integration through the UI and verify it works:
- Settings → Devices & Services → Add Integration → Serac

---

## Project Structure

```
custom_components/serac/
├── __init__.py              # Integration setup, coordinator management
├── config_flow.py           # Configuration UI (3-step flow + options)
├── const.py                 # Constants (massif IDs, domains, defaults)
├── coordinator.py           # Data coordinators (Arome, BRA)
├── sensor.py                # Weather and avalanche sensors
├── weather.py               # Weather entity
├── manifest.json            # Integration metadata
├── strings.json             # English UI text
├── icon.png                 # Integration logo
├── translations/
│   ├── en.json              # English translations
│   └── fr.json              # French translations
└── api/
    ├── openmeteo_client.py  # Open-Meteo API client
    ├── airquality_client.py # Air quality API client
    └── bra_client.py        # BRA API client
```

### Key Files

- **`__init__.py`** - Entry point, sets up coordinators and platforms
- **`config_flow.py`** - Handles user input during setup and configuration
- **`coordinator.py`** - Manages data fetching and updates
- **`sensor.py`** - Creates 51 weather sensors + 8 avalanche sensors per massif
- **`weather.py`** - Weather entity with forecast support
- **`const.py`** - All constants, including massif definitions

---

## Making Changes

### Branch Naming

- `feature/your-feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/what-you-changed` - Documentation
- `refactor/what-you-refactored` - Code refactoring

### Commit Messages

Use conventional commits format:

```
<type>: <description>

[optional body]

Co-Authored-By: Your Name <your.email@example.com>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance

**Examples:**
```bash
git commit -m "feat: Add support for Italian Alps massifs"
git commit -m "fix: Handle missing BRA bulletin gracefully"
git commit -m "docs: Add FAQ section to README"
```

---

## Testing

### Manual Testing

1. **Install your changes** in a test Home Assistant instance
2. **Test all scenarios**:
   - Fresh install with 0 massifs (weather only)
   - Fresh install with 1 massif
   - Fresh install with 3+ massifs
   - Add massifs via Options Flow
   - Remove massifs via Options Flow
   - Change BRA token
   - Invalid coordinates
   - Out-of-season BRA data

### Automated Testing

```bash
# Run unit tests (when available)
pytest tests/

# Run with coverage
pytest --cov=custom_components.serac tests/
```

### Check Logs

Monitor Home Assistant logs while testing:

```bash
tail -f /config/home-assistant.log | grep serac
```

Look for:
- ✅ Successful coordinator updates
- ❌ Error messages
- ⚠️ Warnings about missing data

---

## Submitting Changes

### Before You Submit

- [ ] Code follows the [Code Style](#code-style) below
- [ ] All existing tests pass
- [ ] New features include documentation
- [ ] Commit messages are clear and descriptive
- [ ] You've tested manually in Home Assistant
- [ ] No sensitive data (API keys, tokens) in code

### Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request** on GitHub:
   - Use a clear title: `feat: Add Italian language support`
   - Describe what you changed and why
   - Reference any related issues: `Fixes #123`
   - Add screenshots for UI changes

4. **Respond to feedback**:
   - Maintainers may request changes
   - Update your PR by pushing more commits
   - Discussion is encouraged!

---

## Code Style

### Python

Follow [PEP 8](https://pep8.org/) and Home Assistant conventions:

```python
"""Module docstring."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class MyClass:
    """Class docstring."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        self._hass = hass

    async def async_method(self) -> dict[str, Any]:
        """Method docstring.

        Returns:
            Dictionary with data
        """
        return {"key": "value"}
```

### Key Conventions

- **Type hints** on all function signatures
- **Docstrings** for classes and public methods
- **Async functions** prefixed with `async_`
- **Private attributes** prefixed with `_`
- **Constants** in UPPER_CASE (in const.py)
- **Log at appropriate levels**:
  - `_LOGGER.debug()` - Verbose info
  - `_LOGGER.info()` - Important events
  - `_LOGGER.warning()` - Recoverable issues
  - `_LOGGER.error()` - Errors that should be investigated

### Imports Order

1. Standard library
2. Third-party packages
3. Home Assistant imports
4. Local imports

```python
import asyncio
from datetime import datetime

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
```

---

## Adding New Features

### Adding a New Sensor

1. **Define sensor in `sensor.py`**:
   ```python
   class MyNewSensor(CoordinatorEntity, SensorEntity):
       """My new sensor."""

       @property
       def native_value(self):
           """Return sensor value."""
           return self.coordinator.data.get("my_field")
   ```

2. **Add to sensor setup** in `async_setup_entry()`:
   ```python
   sensors.append(MyNewSensor(coordinator, entity_prefix, "my_sensor"))
   ```

3. **Update coordinator** in `coordinator.py` to fetch data:
   ```python
   data["my_field"] = await self._client.get_my_data()
   ```

### Adding a New Massif

1. **Update `const.py`**:
   ```python
   MASSIF_IDS = {
       # ...existing massifs...
       99: ("New Massif Name", "new-massif"),  # (friendly_name, slug)
   }
   ```

2. **Test** by selecting the new massif during setup

### Adding a Translation

1. **Create `translations/XX.json`** (where XX is language code)
2. **Copy structure from `en.json`**
3. **Translate all strings**
4. **Test** by changing Home Assistant language to XX

### Adding API Support

To add a new data source (e.g., snow depth):

1. **Create client** in `api/my_api_client.py`:
   ```python
   class MyApiClient:
       """Client for my API."""

       async def async_get_data(self) -> dict:
           """Fetch data."""
           # Implementation
   ```

2. **Create coordinator** in `coordinator.py`:
   ```python
   class MyCoordinator(DataUpdateCoordinator):
       """Coordinator for my data."""
   ```

3. **Add to `__init__.py`**:
   ```python
   my_coordinator = MyCoordinator(hass, my_client)
   await my_coordinator.async_config_entry_first_refresh()
   hass.data[DOMAIN][entry.entry_id]["my_coordinator"] = my_coordinator
   ```

4. **Create sensors** in `sensor.py`

---

## Common Development Tasks

### Updating Massif List

Edit `custom_components/serac/const.py`:
```python
MASSIF_IDS = {
    1: ("Chablais", "chablais"),
    2: ("Aravis", "aravis"),
    # Add new massifs here
}
```

### Changing Update Intervals

Edit `coordinator.py`:
```python
# Weather updates
update_interval=timedelta(hours=1)  # Change to hours=2 for 2-hour updates

# Avalanche updates
update_interval=timedelta(hours=6)  # Change to hours=12 for twice-daily updates
```

### Adding Debug Logging

```python
_LOGGER.debug("Fetching data for lat=%s, lon=%s", self._latitude, self._longitude)
```

Enable in Home Assistant:
```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.serac: debug
```

---

## Getting Help

- 💬 **Questions**: [GitHub Discussions](https://github.com/atacamalabs/ha-serac/discussions)
- 🐛 **Bug reports**: [GitHub Issues](https://github.com/atacamalabs/ha-serac/issues)
- 📧 **Email**: hi@atacamalabs.com

---

## Development Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features and priorities. We're currently working on:

1. ✅ Options Flow (v1.2.0-v1.2.6) - COMPLETE
2. ✅ Logo & Branding (v1.3.0) - COMPLETE
3. 📋 Enhanced Documentation (v1.4.0) - IN PROGRESS
4. 🔧 Diagnostics & Code Quality (v1.4.0)
5. ⚠️ Weather Alerts (Vigilance) (v1.5.0)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Serac!** 🏔️

Every contribution, no matter how small, helps make this integration better for the mountain community.
