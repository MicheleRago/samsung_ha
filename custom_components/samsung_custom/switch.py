import logging
import asyncio
from dataclasses import dataclass
from typing import Any, Optional

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CAP_SWITCH, CAP_WASHING_OPTIONS

_LOGGER = logging.getLogger(__name__)

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
        capability="samsungce.autoOpenDoor",
        attribute="autoOpenDoor",
        command_on="setAutoOpenDoor",
        on_value="on",
        off_value="off",
    ),
    SamsungSwitchEntityDescription(
        key="power_cool",
        name="Power Cool",
        icon="mdi:snowflake-alert",
        capability="samsungce.powerCool",
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
        capability="samsungce.powerFreeze",
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
        capability="samsungce.powerFreeze",
        attribute="powerFreeze",
        command_on="setPowerFreeze",
        on_value="on",
        off_value="off",
        on_arg="on",
        off_arg="off",
    ),
    SamsungSwitchEntityDescription(
        key="oven_lamp",
        name="Oven Light",
        icon="mdi:lightbulb",
        capability="samsungce.lamp",
        attribute="brightnessLevel",
        command_on="setBrightnessLevel",
        on_value="high",
        off_value="off",
        on_arg=100,
        off_arg=0,
    ),
    SamsungSwitchEntityDescription(
        key="kids_lock",
        name="Child Lock",
        icon="mdi:lock",
        capability="samsungce.kidsLock",
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
    
    for device_id, device_data in coordinator.data.items():
        components = device_data.get("status", {})
        device_info = device_data.get("device_info", {})
        device_name = device_info.get("name", "Samsung Appliance")
        
        for comp_name, status in components.items():
            name_prefix = f"{device_name} ({comp_name})" if comp_name != "main" else device_name
            
            if CAP_SWITCH in status:
                switches.append(GenericPowerSwitch(coordinator, device_id, comp_name, name_prefix))
                
            for description in SWITCH_TYPES:
                if description.capability in status:
                    switches.append(GenericOptionSwitch(coordinator, device_id, comp_name, name_prefix, description))
            
    async_add_entities(switches)


class GenericPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for power."""

    def __init__(self, coordinator, device_id, component, name):
        super().__init__(coordinator)
        self._device_id = device_id
        self._component = component
        self._device_name = name
        
        comp_prefix = f"_{component}" if component != "main" else ""
        self._attr_unique_id = f"{device_id}{comp_prefix}_power"
        self._attr_name = "Power"
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name.replace(f" ({self._component})", ""),
            "manufacturer": "Samsung",
        }

    @property
    def is_on(self):
        """Return true if device is on."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return False
        return data.get(CAP_SWITCH, {}).get("switch", {}).get("value") == "on"

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.coordinator.api.execute_command(self._device_id, self._component, CAP_SWITCH, "on")
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.coordinator.api.execute_command(self._device_id, self._component, CAP_SWITCH, "off")
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()


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
        self._on_arg = description.on_arg if description.on_arg is not None else ([self._on_value] if self._on_value is not None else [])
        self._off_arg = description.off_arg if description.off_arg is not None else ([self._off_value] if self._off_value is not None else [])
        
        comp_prefix = f"_{component}" if component != "main" else ""
        self._attr_unique_id = f"{device_id}{comp_prefix}_{description.capability}_{description.attribute}"
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name.replace(f" ({self._component})", ""),
            "manufacturer": "Samsung",
        }

    @property
    def is_on(self):
        """Return true if switch is on."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return False
        val = data.get(self.entity_description.capability, {}).get(self.entity_description.attribute, {}).get("value")
        
        if isinstance(val, dict) and "value" in val:
            val = val.get("value")
            
        return val == self._on_value

    async def async_turn_on(self, **kwargs):
        """Turn the option on."""
        await self.coordinator.api.execute_command(self._device_id, self._component, self.entity_description.capability, self._command_on, self._on_arg)
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the option off."""
        await self.coordinator.api.execute_command(self._device_id, self._component, self.entity_description.capability, self._command_off, self._off_arg)
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()
