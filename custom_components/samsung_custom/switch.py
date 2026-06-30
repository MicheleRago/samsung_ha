from dataclasses import dataclass
from typing import Any, Optional

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CAP_AUTO_OPEN_DOOR,
    CAP_KIDS_LOCK,
    CAP_POWER_COOL,
    CAP_POWER_FREEZE,
    CAP_SWITCH,
    CAP_WASHING_OPTIONS,
    DOMAIN,
)
from .entity import (
    capability_value,
    component_prefix,
    component_status,
    iter_component_statuses,
    refresh_after_command,
    samsung_device_info,
)

@dataclass(kw_only=True)
class SamsungSwitchEntityDescription(SwitchEntityDescription):
    """Class describing Samsung switch entities."""
    capability: str
    attribute: str
    command_on: str
    command_off: Optional[str] = None
    on_value: Any = "on"
    off_value: Any = "off"
    on_arg: Any = None
    off_arg: Any = None

SWITCH_TYPES: tuple[SamsungSwitchEntityDescription, ...] = (
    SamsungSwitchEntityDescription(
        key="half_load",
        name="Half Load",
        icon="mdi:washing-machine",
        capability=CAP_WASHING_OPTIONS,
        attribute="selectedZone",
        command_on="setSelectedZone",
        on_value="lower",
        off_value="all",
    ),
    SamsungSwitchEntityDescription(
        key="speed_booster",
        name="Speed Booster",
        icon="mdi:fast-forward",
        capability=CAP_WASHING_OPTIONS,
        attribute="speedBooster",
        command_on="setSpeedBooster",
        on_value=True,
        off_value=False,
    ),
    SamsungSwitchEntityDescription(
        key="sanitize",
        name="Sanitization",
        icon="mdi:water-boiler",
        capability=CAP_WASHING_OPTIONS,
        attribute="sanitize",
        command_on="setSanitize",
        on_value=True,
        off_value=False,
    ),
    SamsungSwitchEntityDescription(
        key="auto_open_door",
        name="Auto Release Dry",
        icon="mdi:door-open",
        capability=CAP_AUTO_OPEN_DOOR,
        attribute="autoOpenDoor",
        command_on="setAutoOpenDoor",
        on_value="on",
        off_value="off",
    ),
    SamsungSwitchEntityDescription(
        key="power_cool",
        name="Power Cool",
        icon="mdi:snowflake-alert",
        capability=CAP_POWER_COOL,
        attribute="activated",
        command_on="activate",
        command_off="deactivate",
        on_value=True,
        off_value=False,
        on_arg=[],
        off_arg=[],
    ),
    SamsungSwitchEntityDescription(
        key="power_freeze",
        name="Power Freeze",
        icon="mdi:snowflake-alert",
        capability=CAP_POWER_FREEZE,
        attribute="activated",
        command_on="activate",
        command_off="deactivate",
        on_value=True,
        off_value=False,
        on_arg=[],
        off_arg=[],
    ),
    SamsungSwitchEntityDescription(
        key="fridge_power_freeze",
        name="Power Freeze",
        icon="mdi:snowflake-melt",
        capability=CAP_POWER_FREEZE,
        attribute="powerFreeze",
        command_on="setPowerFreeze",
        on_value="on",
        off_value="off",
        on_arg="on",
        off_arg="off",
    ),

    SamsungSwitchEntityDescription(
        key="kids_lock",
        name="Child Lock",
        icon="mdi:lock",
        capability=CAP_KIDS_LOCK,
        attribute="lockState",
        command_on="setLockState",
        on_value="locked",
        off_value="unlocked",
        on_arg="locked",
        off_arg="unlocked",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    switches = []
    
    for device_id, component, status, name_prefix in iter_component_statuses(coordinator):
        if CAP_SWITCH in status:
            switches.append(GenericPowerSwitch(coordinator, device_id, component, name_prefix))

        for description in SWITCH_TYPES:
            if description.capability in status:
                switches.append(GenericOptionSwitch(coordinator, device_id, component, name_prefix, description))
            
    async_add_entities(switches)


class GenericPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for power."""

    def __init__(self, coordinator, device_id, component, name):
        super().__init__(coordinator)
        self._device_id = device_id
        self._component = component
        self._device_name = name
        
        comp_prefix = component_prefix(component)
        self._attr_unique_id = f"{device_id}{comp_prefix}_power"
        self._attr_name = "Power"
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return samsung_device_info(self._device_id, self._device_name, self._component)

    @property
    def is_on(self):
        """Return true if device is on."""
        data = component_status(self.coordinator, self._device_id, self._component)
        if not data:
            return False
        return capability_value(data, CAP_SWITCH, "switch") == "on"

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._async_set_power("on")

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self._async_set_power("off")

    async def _async_set_power(self, command: str) -> None:
        """Send a power command and refresh state."""
        await self.coordinator.api.execute_command(
            self._device_id,
            self._component,
            CAP_SWITCH,
            command,
        )
        await refresh_after_command(self.coordinator)


class GenericOptionSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for generic options."""
    entity_description: SamsungSwitchEntityDescription

    def __init__(self, coordinator, device_id, component, device_name, description: SamsungSwitchEntityDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._component = component
        self._device_name = device_name
        
        self._command_on = description.command_on
        self._command_off = description.command_off if description.command_off else description.command_on
        self._on_value = description.on_value
        self._off_value = description.off_value
        if description.on_arg is not None:
            self._on_arg = description.on_arg if isinstance(description.on_arg, list) else [description.on_arg]
        else:
            self._on_arg = [self._on_value] if self._on_value is not None else []
            
        if description.off_arg is not None:
            self._off_arg = description.off_arg if isinstance(description.off_arg, list) else [description.off_arg]
        else:
            self._off_arg = [self._off_value] if self._off_value is not None else []
        
        comp_prefix = component_prefix(component)
        self._attr_unique_id = f"{device_id}{comp_prefix}_{description.capability}_{description.attribute}"
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return samsung_device_info(self._device_id, self._device_name, self._component)

    @property
    def is_on(self):
        """Return true if switch is on."""
        data = component_status(self.coordinator, self._device_id, self._component)
        if not data:
            return False
        val = capability_value(
            data,
            self.entity_description.capability,
            self.entity_description.attribute,
        )

        return val == self._on_value

    async def async_turn_on(self, **kwargs):
        """Turn the option on."""
        await self._async_set_option(self._command_on, self._on_arg)

    async def async_turn_off(self, **kwargs):
        """Turn the option off."""
        await self._async_set_option(self._command_off, self._off_arg)

    async def _async_set_option(self, command: str, arguments: list[Any]) -> None:
        """Send an option command and refresh state."""
        await self.coordinator.api.execute_command(
            self._device_id,
            self._component,
            self.entity_description.capability,
            command,
            arguments,
        )
        await refresh_after_command(self.coordinator)
