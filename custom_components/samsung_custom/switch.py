import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CAP_SWITCH, CAP_WASHING_OPTIONS

_LOGGER = logging.getLogger(__name__)

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
                
            if CAP_WASHING_OPTIONS in status:
                switches.append(GenericOptionSwitch(coordinator, device_id, comp_name, name_prefix, CAP_WASHING_OPTIONS, "selectedZone", "setSelectedZone", "Half Load", "mdi:washing-machine", on_value="lower", off_value="all"))
                switches.append(GenericOptionSwitch(coordinator, device_id, comp_name, name_prefix, CAP_WASHING_OPTIONS, "speedBooster", "setSpeedBooster", "Speed Booster", "mdi:fast-forward", on_value=True, off_value=False))
                switches.append(GenericOptionSwitch(coordinator, device_id, comp_name, name_prefix, CAP_WASHING_OPTIONS, "sanitize", "setSanitize", "Sanitization", "mdi:water-boiler", on_value=True, off_value=False))
                
            # Asciugatura rilascio automatico
            if "samsungce.autoOpenDoor" in status:
                switches.append(GenericOptionSwitch(coordinator, device_id, comp_name, name_prefix, "samsungce.autoOpenDoor", "autoOpenDoor", "setAutoOpenDoor", "Auto Release Dry", "mdi:door-open", on_value="on", off_value="off"))

            # Frigo options
            if "samsungce.powerCool" in status:
                switches.append(GenericOptionSwitch(coordinator, device_id, comp_name, name_prefix, "samsungce.powerCool", "activated", "activate", "Power Cool", "mdi:snowflake-alert", on_value=True, off_value=False, command_off="deactivate", on_arg=[], off_arg=[]))
            if "samsungce.powerFreeze" in status:
                switches.append(GenericOptionSwitch(coordinator, device_id, comp_name, name_prefix, "samsungce.powerFreeze", "activated", "activate", "Power Freeze", "mdi:snowflake-alert", on_value=True, off_value=False, command_off="deactivate", on_arg=[], off_arg=[]))

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
        """Return true if switch is on."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return False
        return data.get(CAP_SWITCH, {}).get("switch", {}).get("value") == "on"

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        import asyncio
        await self.coordinator.api.execute_command(self._device_id, self._component, CAP_SWITCH, "on")
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        import asyncio
        await self.coordinator.api.execute_command(self._device_id, self._component, CAP_SWITCH, "off")
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()


class GenericOptionSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for generic options."""

    def __init__(self, coordinator, device_id, component, device_name, capability, attribute, command, name, icon, on_value="on", off_value="off", command_off=None, on_arg=None, off_arg=None):
        super().__init__(coordinator)
        self._device_id = device_id
        self._component = component
        self._device_name = device_name
        self._capability = capability
        self._attribute = attribute
        self._command = command
        self._command_off = command_off if command_off else command
        self._on_value = on_value
        self._off_value = off_value
        self._on_arg = on_arg if on_arg is not None else ([on_value] if on_value is not None else [])
        self._off_arg = off_arg if off_arg is not None else ([off_value] if off_value is not None else [])
        
        comp_prefix = f"_{component}" if component != "main" else ""
        self._attr_unique_id = f"{device_id}{comp_prefix}_{capability}_{attribute}"
        self._attr_name = name
        self._attr_icon = icon
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
        val = data.get(self._capability, {}).get(self._attribute, {}).get("value")
        
        # Some values are dictionaries like {"value": False, "settable": [False, True]}
        if isinstance(val, dict) and "value" in val:
            val = val.get("value")
            
        return val == self._on_value

    async def async_turn_on(self, **kwargs):
        """Turn the option on."""
        import asyncio
        await self.coordinator.api.execute_command(self._device_id, self._component, self._capability, self._command, self._on_arg)
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the option off."""
        import asyncio
        await self.coordinator.api.execute_command(self._device_id, self._component, self._capability, self._command_off, self._off_arg)
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()
