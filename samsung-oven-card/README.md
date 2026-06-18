# Samsung Oven Card

A beautifully animated Lovelace custom card for Samsung Smart Ovens in Home Assistant, designed to look identical to the Samsung Fridge Card.

## Installation

1. Copy the `samsung-oven-card.js` file to your Home Assistant `www/` directory.
   - Using File Editor or SSH: `cp samsung-oven-card.js /config/www/`
2. Go to **Settings > Dashboards > 3 dots (top right) > Resources**.
3. Add a new resource:
   - URL: `/local/samsung-oven-card.js`
   - Resource type: `JavaScript Module`
4. Refresh your Home Assistant dashboard.

## Configuration

In your Lovelace Dashboard, add a new "Manual" card and paste the following YAML. Make sure to replace the entity names with the actual entity IDs of your oven.

```yaml
type: custom:samsung-oven-card
name: Forno Samsung
icon: mdi:stove
entities:
  oven_state: sensor.forno_oven_machine_state
  current_temp: sensor.forno_temperature
  target_temp: number.forno_oven_target_temperature
  cook_time: number.forno_oven_cook_time
  oven_mode: select.forno_oven_mode
  start_btn: button.forno_start
  pause_btn: button.forno_pause
  stop_btn: button.forno_stop
  light: switch.forno_light
  remote_control: sensor.forno_remote_control
```

### Features
- **Dynamic Header**: The oven icon glows and pulses with a heating animation when the oven is running.
- **Smart Control Indicator**: Shows a remote icon in the corner indicating if physical Smart Control is enabled.
- **Unified Controls**: Set your Target Temperature, Cook Time, and Cooking Mode before hitting start.
- **Smart Actions**: The Start button is only shown when the oven is idle. When running, Pause and Stop buttons appear.
