# Samsung Washer Card

Custom Lovelace card for Samsung SmartThings washers exposed by this integration.

## Installation

1. Copy `samsung-washer-card.js` to your Home Assistant `www/` directory.
2. Add a dashboard resource:
   - URL: `/local/samsung-washer-card.js`
   - Resource type: `JavaScript Module`
3. Refresh the Home Assistant dashboard.

## Configuration

Add a manual Lovelace card and replace the entity IDs with yours.

```yaml
type: custom:samsung-washer-card
name: Lavatrice Samsung
icon: mdi:washing-machine
entities:
  machine_state: sensor.lavatrice_washer_state
  course: select.lavatrice_washer_course
  run_btn: button.lavatrice_run
  pause_btn: button.lavatrice_pause
  stop_btn: button.lavatrice_stop
  power: switch.lavatrice_power
  remote_control: sensor.lavatrice_remote_control
  door: binary_sensor.lavatrice_door
  child_lock: switch.lavatrice_child_lock
```

Optional entities, if your washer exposes them:

```yaml
  job_state: sensor.lavatrice_job_state
  remaining_time: sensor.lavatrice_remaining_time
  completion_time: sensor.lavatrice_completion_time
```

Only `machine_state` is required. Remove any line for entities your washer does not expose.

## Behavior

- When idle, the card shows cycle selection, available options, power, and start.
- When running or paused, it hides setup controls and shows progress plus pause/stop.
- When the door is open, power is off, or Smart Control is disabled, it hides start and shows a warning.
