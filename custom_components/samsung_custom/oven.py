"""Helpers for Samsung oven entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .const import (
    CAP_OVEN_DOOR,
    CAP_OVEN_MODE,
    CAP_OVEN_OPERATING_STATE,
    CAP_OVEN_SETPOINT,
    CAP_REMOTE_CONTROL,
    DOMAIN,
    get_oven_operating_state,
    normalize_oven_mode_code,
)

DEFAULT_OVEN_COOK_TIME = 30.0
DEFAULT_OVEN_MODE = "Bake"
DEFAULT_OVEN_TEMPERATURE = 200
OVEN_PENDING_STATE_DATA_KEY = "pending_oven_state"

OVEN_ACTIVE_MACHINE_STATES = {"running", "paused"}
OVEN_READY_JOB_STATES = {None, "ready", "finished"}


@dataclass(frozen=True)
class OvenStartSettings:
    """Values needed to start a Samsung oven cycle."""

    mode: str
    temperature: int
    cook_time_minutes: float
    cook_time_seconds: int
    operation_time: str
    remote_enabled: Any
    door_state: Any


def component_status(coordinator, device_id: str, component: str) -> dict[str, Any]:
    """Return cached SmartThings status for a device component."""
    return coordinator.data.get(device_id, {}).get("status", {}).get(component, {})


def pending_oven_state(hass, device_id: str, create: bool = False) -> dict[str, Any]:
    """Return the local, not-yet-started oven settings for a device."""
    domain_data = hass.data.setdefault(DOMAIN, {}) if create else hass.data.get(DOMAIN, {})
    if create:
        return domain_data.setdefault(OVEN_PENDING_STATE_DATA_KEY, {}).setdefault(device_id, {})
    return domain_data.get(OVEN_PENDING_STATE_DATA_KEY, {}).get(device_id, {})


def cache_oven_setting(hass, device_id: str, key: str, value: Any) -> None:
    """Store a pending oven setting until the user presses Start."""
    pending_oven_state(hass, device_id, create=True)[key] = value


def cached_oven_setting(hass, device_id: str, key: str, default: Any = None) -> Any:
    """Read a pending oven setting."""
    return pending_oven_state(hass, device_id).get(key, default)


def oven_is_waiting_for_start(status: dict[str, Any]) -> bool:
    """Return true when oven settings should be cached instead of sent now."""
    oven_state = get_oven_operating_state(status)
    machine_state = oven_state.get("machineState", {}).get("value")
    job_state = oven_state.get("ovenJobState", {}).get("value")
    return machine_state not in OVEN_ACTIVE_MACHINE_STATES and job_state in OVEN_READY_JOB_STATES


def format_operation_time(cook_time_minutes: float) -> str:
    """Convert minutes to SmartThings HH:MM:SS operation time."""
    total_seconds = operation_seconds(cook_time_minutes)

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def operation_seconds(cook_time_minutes: float) -> int:
    """Convert minutes to whole seconds for the legacy oven start command."""
    return max(0, int(_float_value(cook_time_minutes, DEFAULT_OVEN_COOK_TIME) * 60))


def _float_value(value: Any, default: float) -> float:
    """Return a float while tolerating unavailable SmartThings values."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def oven_start_settings(hass, coordinator, device_id: str, component: str) -> OvenStartSettings:
    """Read current and pending oven settings for the Start command."""
    status = component_status(coordinator, device_id, component)
    pending = pending_oven_state(hass, device_id)

    raw_mode = status.get(CAP_OVEN_MODE, {}).get("ovenMode", {}).get("value", DEFAULT_OVEN_MODE)
    raw_temperature = status.get(CAP_OVEN_SETPOINT, {}).get("ovenSetpoint", {}).get("value", DEFAULT_OVEN_TEMPERATURE)

    mode = normalize_oven_mode_code(pending.get("mode", raw_mode)) or DEFAULT_OVEN_MODE
    temperature = int(_float_value(pending.get("temp", raw_temperature), DEFAULT_OVEN_TEMPERATURE))
    cook_time_minutes = _float_value(pending.get("cook_time", DEFAULT_OVEN_COOK_TIME), DEFAULT_OVEN_COOK_TIME)

    return OvenStartSettings(
        mode=mode,
        temperature=temperature,
        cook_time_minutes=cook_time_minutes,
        cook_time_seconds=operation_seconds(cook_time_minutes),
        operation_time=format_operation_time(cook_time_minutes),
        remote_enabled=status.get(CAP_REMOTE_CONTROL, {}).get("remoteControlEnabled", {}).get("value"),
        door_state=status.get(CAP_OVEN_DOOR, {}).get("doorState", {}).get("value"),
    )


def oven_start_commands(component: str, settings: OvenStartSettings) -> list[dict[str, Any]]:
    """Build the SmartThings command batch that starts this oven model."""
    return [
        {
            "component": component,
            "capability": CAP_OVEN_MODE,
            "command": "setOvenMode",
            "arguments": [settings.mode],
        },
        {
            "component": component,
            "capability": CAP_OVEN_SETPOINT,
            "command": "setOvenSetpoint",
            "arguments": [settings.temperature],
        },
        {
            "component": component,
            "capability": CAP_OVEN_OPERATING_STATE,
            "command": "setOperationTime",
            "arguments": [settings.operation_time],
        },
        {
            "component": component,
            "capability": CAP_OVEN_OPERATING_STATE,
            "command": "start",
            "arguments": [],
        },
    ]
