import json
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN, CAP_OPERATING_STATE, CAP_WASHER_OPERATING_STATE,
    CAP_DRYER_OPERATING_STATE, CAP_OVEN_OPERATING_STATE,
    CAP_OVEN_OPERATING_STATE_STANDARD,
    OVEN_OPERATING_STATE_CAPABILITIES
)
from .entity import (
    component_prefix,
    iter_component_statuses,
    refresh_after_command,
    samsung_device_info,
)
from .oven import OvenStartSettings, oven_start_commands, oven_start_settings

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the button platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    buttons = []
    
    for device_id, component, status, name in iter_component_statuses(coordinator):
        # Check which capability this device uses for operating state.
        cap = None
        if CAP_OPERATING_STATE in status:
            cap = CAP_OPERATING_STATE
        elif CAP_WASHER_OPERATING_STATE in status:
            cap = CAP_WASHER_OPERATING_STATE
        elif CAP_DRYER_OPERATING_STATE in status:
            cap = CAP_DRYER_OPERATING_STATE
        elif any(oven_cap in status for oven_cap in OVEN_OPERATING_STATE_CAPABILITIES):
            cap = CAP_OVEN_OPERATING_STATE

        if cap:
            buttons.append(
                GenericCommandButton(
                    coordinator,
                    device_id,
                    component,
                    name,
                    cap,
                    "Run",
                    "run",
                    "mdi:play",
                )
            )
            buttons.append(
                GenericCommandButton(
                    coordinator,
                    device_id,
                    component,
                    name,
                    cap,
                    "Pause",
                    "pause",
                    "mdi:pause",
                )
            )
            buttons.append(
                GenericCommandButton(
                    coordinator,
                    device_id,
                    component,
                    name,
                    cap,
                    "Stop",
                    "stop",
                    "mdi:stop",
                )
            )

    async_add_entities(buttons)

class GenericCommandButton(CoordinatorEntity, ButtonEntity):
    """Button for sending commands."""

    def __init__(self, coordinator, device_id, component, device_name, capability, btn_name, command_arg, icon):
        super().__init__(coordinator)
        self._device_id = device_id
        self._component = component
        self._device_name = device_name
        self._capability = capability
        self._command_arg = command_arg
        
        comp_prefix = component_prefix(component)
        self._attr_unique_id = f"{device_id}{comp_prefix}_{capability}_{command_arg}"
        self._attr_name = btn_name
        self._attr_icon = icon
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return samsung_device_info(self._device_id, self._device_name, self._component)

    async def async_press(self) -> None:
        """Handle the button press."""
        if self._capability == CAP_OVEN_OPERATING_STATE:
            await self._async_press_oven()
        else:
            await self.coordinator.api.execute_command(
                self._device_id,
                self._component,
                self._capability,
                "setMachineState",
                [self._command_arg],
            )
        await refresh_after_command(self.coordinator)

    async def _async_press_oven(self) -> None:
        """Handle oven-specific run/pause/stop commands."""
        command = "start" if self._command_arg == "run" else self._command_arg
        if command != "start":
            await self.coordinator.api.execute_command(
                self._device_id,
                self._component,
                CAP_OVEN_OPERATING_STATE,
                command,
            )
            return

        settings = oven_start_settings(
            self.coordinator.hass,
            self.coordinator,
            self._device_id,
            self._component,
        )
        self._warn_if_oven_start_may_fail(settings)

        if settings.mode == "FanConventional":
            await self._async_start_oven_batch(settings)
            return

        await self._async_start_oven_legacy(settings)

    def _warn_if_oven_start_may_fail(self, settings: OvenStartSettings) -> None:
        """Log local preconditions that commonly block remote oven starts."""
        if str(settings.remote_enabled).lower() in ("false", "off", "disabled"):
            _LOGGER.warning(
                "Samsung oven remote control is disabled; the start command may be ignored"
            )
        if settings.door_state == "open":
            _LOGGER.warning(
                "Samsung oven door is open; the start command may be ignored"
            )

    async def _async_start_oven_batch(self, settings: OvenStartSettings) -> None:
        """Start FanConventional using the modern SmartThings batch payload."""
        commands = oven_start_commands(self._component, settings)
        payload = {"commands": commands}
        _LOGGER.error(
            "OVEN SMARTTHINGS REQUEST: device_id=%s method=batch mode=%s operation_time=%s temp=%s payload=%s",
            self._device_id,
            settings.mode,
            settings.operation_time,
            settings.temperature,
            json.dumps(payload, ensure_ascii=False),
        )
        await self.coordinator.api.execute_commands(self._device_id, commands)

    async def _async_start_oven_legacy(self, settings: OvenStartSettings) -> None:
        """Start all non-FanConventional oven modes using the legacy payload."""
        legacy_command = {
            "component": self._component,
            "capability": CAP_OVEN_OPERATING_STATE_STANDARD,
            "command": "start",
            "arguments": [
                settings.mode,
                settings.cook_time_seconds,
                settings.temperature,
            ],
        }
        _LOGGER.error(
            "OVEN SMARTTHINGS REQUEST: device_id=%s method=legacy mode=%s cook_time=%ss temp=%s payload=%s",
            self._device_id,
            settings.mode,
            settings.cook_time_seconds,
            settings.temperature,
            json.dumps([legacy_command], ensure_ascii=False),
        )
        await self.coordinator.api.execute_legacy_commands(
            self._device_id,
            [legacy_command],
        )
