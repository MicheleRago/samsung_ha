"""Shared helpers for Samsung Custom Appliance entities."""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from typing import Any

from .const import DOMAIN

REFRESH_DELAY_SECONDS = 2
DEFAULT_DEVICE_NAME = "Samsung Appliance"


def component_prefix(component: str) -> str:
    """Return a stable unique-id suffix for a component."""
    return f"_{component}" if component != "main" else ""


def component_name(device_name: str, component: str) -> str:
    """Return the display name used for a component-backed entity."""
    return f"{device_name} ({component})" if component != "main" else device_name


def base_device_name(device_name: str, component: str) -> str:
    """Return the device name without a component suffix."""
    suffix = f" ({component})"
    if component != "main" and device_name.endswith(suffix):
        return device_name[: -len(suffix)]
    return device_name


def device_name_from_data(device_data: dict[str, Any]) -> str:
    """Return the SmartThings device name from cached coordinator data."""
    return device_data.get("device_info", {}).get("name", DEFAULT_DEVICE_NAME)


def iter_component_statuses(coordinator) -> Iterator[tuple[str, str, dict[str, Any], str]]:
    """Yield device id, component, status and component display name."""
    for device_id, device_data in coordinator.data.items():
        device_name = device_name_from_data(device_data)
        for component, status in device_data.get("status", {}).items():
            yield device_id, component, status, component_name(device_name, component)


def component_status(coordinator, device_id: str, component: str) -> dict[str, Any]:
    """Return cached SmartThings status for a device component."""
    return coordinator.data.get(device_id, {}).get("status", {}).get(component, {})


def capability_value(
    status: dict[str, Any],
    capability: str,
    attribute: str,
    default: Any = None,
) -> Any:
    """Return a SmartThings capability attribute value."""
    value = status.get(capability, {}).get(attribute, {}).get("value", default)
    if isinstance(value, dict) and "value" in value:
        return value.get("value", default)
    return value


def samsung_device_info(device_id: str, device_name: str, component: str) -> dict[str, Any]:
    """Return Home Assistant device registry info."""
    return {
        "identifiers": {(DOMAIN, device_id)},
        "name": base_device_name(device_name, component),
        "manufacturer": "Samsung",
    }


async def refresh_after_command(coordinator) -> None:
    """Refresh coordinator data after SmartThings has applied a command."""
    await asyncio.sleep(REFRESH_DELAY_SECONDS)
    await coordinator.async_request_refresh()
