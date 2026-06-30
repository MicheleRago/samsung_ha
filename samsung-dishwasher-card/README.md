# Samsung Dishwasher Card

Custom Lovelace card for Samsung SmartThings dishwashers exposed by this integration.

## Installation

1. Copy `samsung-dishwasher-card.js` to your Home Assistant `www/` directory.
2. Add a dashboard resource:
   - URL: `/local/samsung-dishwasher-card.js`
   - Resource type: `JavaScript Module`
3. Refresh the Home Assistant dashboard.

## Configuration

Add a manual Lovelace card and replace the entity IDs with yours.

```yaml
type: custom:samsung-dishwasher-card
name: Lavastoviglie Samsung
icon: mdi:dishwasher
entities:
  machine_state: sensor.lavastoviglie_machine_state
  job_state: sensor.lavastoviglie_job_state
  remaining_time: sensor.lavastoviglie_remaining_time
  completion_time: sensor.lavastoviglie_dishwasher_completion_time
  course: select.lavastoviglie_dishwasher_course
  run_btn: button.lavastoviglie_run
  pause_btn: button.lavastoviglie_pause
  stop_btn: button.lavastoviglie_stop
  power: switch.lavastoviglie_power
  remote_control: sensor.lavastoviglie_remote_control
  door: binary_sensor.lavastoviglie_door
  half_load: switch.lavastoviglie_half_load
  speed_booster: switch.lavastoviglie_speed_booster
  sanitize: switch.lavastoviglie_sanitization
  auto_open_door: switch.lavastoviglie_auto_release_dry
```

All entities except `machine_state` are optional. If your dishwasher does not expose one of the switches or sensors, remove that line from the configuration.

## Notes

Samsung usually requires Smart Control / Remote Control to be enabled on the dishwasher panel before Home Assistant can start a cycle remotely.
