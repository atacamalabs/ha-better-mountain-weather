# Serac Automation Blueprints

Pre-built automation blueprints for common Serac use cases. Import these directly into Home Assistant for quick setup!

## Available Blueprints

### 1. Weather Alert Notification
**File**: `serac_weather_alert_notification.yaml`

Send mobile notifications when weather alerts are detected.

**Import URL**:
```
https://github.com/atacamalabs/ha-serac/blob/main/blueprints/automation/serac_weather_alert_notification.yaml
```

**Features**:
- Triggers on any active alert
- Customizable notification service
- Optional detailed alert information
- Works with all Serac binary sensors

**Use Cases**:
- Get notified of any weather alert
- Monitor specific alert types (active, orange, red)

---

### 2. Dangerous Weather TTS Announcement
**File**: `serac_dangerous_weather_tts.yaml`

Make text-to-speech announcements for dangerous weather conditions.

**Import URL**:
```
https://github.com/atacamalabs/ha-serac/blob/main/blueprints/automation/serac_dangerous_weather_tts.yaml
```

**Features**:
- Triggers on orange/red alerts
- Multi-language support (EN, FR, DE, IT, ES)
- Customizable media player
- Detailed alert information in announcement

**Use Cases**:
- Audible alerts at home
- Announcements in multiple rooms
- Emergency notifications

---

### 3. Avalanche Risk Alert
**File**: `serac_avalanche_risk_alert.yaml`

Send notifications when avalanche risk reaches dangerous levels.

**Import URL**:
```
https://github.com/atacamalabs/ha-serac/blob/main/blueprints/automation/serac_avalanche_risk_alert.yaml
```

**Features**:
- Customizable risk threshold (2-5)
- Optional accidental risk information
- Works with any Serac avalanche sensor
- Massif-specific alerts

**Use Cases**:
- Mountain activity planning
- Backcountry safety
- Ski touring alerts

---

### 4. Red Alert Visual Warning
**File**: `serac_red_alert_visual_warning.yaml`

Flash lights red when extreme weather conditions are detected.

**Import URL**:
```
https://github.com/atacamalabs/ha-serac/blob/main/blueprints/automation/serac_red_alert_visual_warning.yaml
```

**Features**:
- Flashes lights red on red alerts
- Customizable flash pattern
- Optional critical mobile notification
- Targets any light entities

**Use Cases**:
- Emergency visual alerts
- Attention-grabbing warnings
- Critical weather notifications

---

## How to Import

### Method 1: UI Import (Recommended)

1. **Copy the Import URL** for the blueprint you want
2. Go to **Settings** → **Automations & Scenes** → **Blueprints**
3. Click the **blue "Import Blueprint"** button (bottom right)
4. **Paste the URL** and click **Preview**
5. Click **Import Blueprint**
6. The blueprint is now available in your automations!

### Method 2: Manual Download

1. Download the `.yaml` file from GitHub
2. Place it in `config/blueprints/automation/serac/`
3. Restart Home Assistant
4. Blueprint will appear in automation creation

---

## Using Blueprints

After importing:

1. Go to **Settings** → **Automations & Scenes**
2. Click **Create Automation** → **Start with a Blueprint**
3. Select the Serac blueprint you want
4. Fill in the required fields:
   - Select your Serac sensors
   - Choose notification services
   - Customize thresholds and options
5. Give it a name and **Save**

---

## Blueprint Requirements

### Required Serac Sensors

Different blueprints require different sensors:

**Weather Alert Notification**:
- `binary_sensor.serac_{prefix}_has_active_alert` (any alert)
- `binary_sensor.serac_{prefix}_has_orange_alert` (dangerous)
- `binary_sensor.serac_{prefix}_has_red_alert` (extreme)

**Dangerous Weather TTS**:
- `binary_sensor.serac_{prefix}_has_orange_alert`

**Avalanche Risk Alert**:
- `sensor.serac_{prefix}_{massif}_avalanche_risk_today`

**Red Alert Visual Warning**:
- `binary_sensor.serac_{prefix}_has_red_alert`

### Required Services

- **Mobile notifications**: `notify.mobile_app_*` or similar
- **TTS announcements**: `tts.google_translate_say` or similar
- **Light control**: Any compatible light entities

---

## Customization

All blueprints can be customized after import:

1. Create automation from blueprint
2. Click **⋮** (three dots) → **Edit in YAML**
3. Modify triggers, conditions, or actions
4. Save changes

---

## Example Configurations

### Weather Alert Notification

```yaml
Alert Sensor: binary_sensor.serac_home_has_active_alert
Notification Service: notify.mobile_app_iphone
Notification Title: ⚠️ Weather Alert
Include Alert Details: true
```

### Dangerous Weather TTS

```yaml
Orange/Red Alert Sensor: binary_sensor.serac_home_has_orange_alert
Media Player: media_player.living_room_speaker
TTS Service: tts.google_translate_say
Announcement Language: en
```

### Avalanche Risk Alert

```yaml
Avalanche Risk Sensor: sensor.serac_chamonix_mont_blanc_avalanche_risk_today
Risk Threshold: 3 (Considerable - Orange)
Notification Service: notify.mobile_app_iphone
Include Accidental Risk Info: true
```

### Red Alert Visual Warning

```yaml
Red Alert Sensor: binary_sensor.serac_home_has_red_alert
Lights: light.all_lights
Flash Pattern: long
Send Notification: true
Notification Service: notify.mobile_app_iphone
```

---

## Troubleshooting

### Blueprint doesn't appear after import
- Restart Home Assistant
- Check the blueprint file syntax
- Verify the import URL is correct

### Automation not triggering
- Check that Serac sensors are updating (verify in Developer Tools → States)
- Verify the selected sensor entity ID is correct
- Check automation traces (Settings → Automations → Select automation → Traces)

### Notification not received
- Test notification service: Developer Tools → Services → notify.mobile_app_*
- Verify device is connected to Home Assistant
- Check notification permissions on mobile device

---

## Contributing

Have ideas for new blueprints? [Open an issue](https://github.com/atacamalabs/ha-serac/issues) or submit a pull request!

---

## Links

- **Main Repository**: https://github.com/atacamalabs/ha-serac
- **Documentation**: [README.md](../README.md)
- **Issues**: https://github.com/atacamalabs/ha-serac/issues
