# Samsung Washer Card

Custom Lovelace card for Samsung SmartThings washers exposed by this integration.

## Installation

1. Copy `samsung-washer-card.js` to your Home Assistant `www/` directory.
2. Add a dashboard resource:
   - URL: `/local/samsung-washer-card.js`
   - Resource type: `JavaScript Module`
3. Refresh the Home Assistant dashboard.

## Configuration

Add a manual Lovelace card. If your washer entities start with the same prefix, use the short form:

```yaml
type: custom:samsung-washer-card
name: Lavatrice Samsung
icon: mdi:washing-machine
entity_prefix: lavatrice
```

This expands to IDs such as `sensor.lavatrice_washer_state`, `select.lavatrice_washer_course`, and `button.lavatrice_run`.
For the cycle dropdown, the card also tries common alternatives such as `select.lavatrice_washer_cycle`, `select.lavatrice_course`, and `select.lavatrice_cycle`.

If your entity IDs do not follow that pattern, use explicit entities:

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

You can also combine both forms and override only some entities:

```yaml
type: custom:samsung-washer-card
name: Lavatrice Samsung
entity_prefix: lavatrice
entities:
  door: binary_sensor.lavatrice_oblo
  course: select.lavatrice_programma
```

Only `machine_state` is required when using explicit entities. Remove any line for entities your washer does not expose.

## Behavior

- When idle, the card shows cycle selection, available options, power, and start.
- When running or paused, it hides setup controls and shows progress plus pause/stop.
- When the door is open, power is off, or Smart Control is disabled, it keeps the controls visible and shows a warning.
