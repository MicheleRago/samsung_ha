import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CAP_SWITCH

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    switches = []
    
    for device_id, device_data in coordinator.data.items():
        status = device_data.get("status", {})
        device_info = device_data.get("device_info", {})
        name = device_info.get("name", "Samsung Appliance")
        
        if CAP_SWITCH in status:
            switches.append(GenericPowerSwitch(coordinator, device_id, name))
            
    async_add_entities(switches)

class GenericPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for power."""

    def __init__(self, coordinator, device_id, device_name):
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{device_id}_power"
        self._attr_name = "Power"
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Samsung",
        }

    @property
    def is_on(self):
        """Return true if switch is on."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {})
        if not data:
            return False
        return data.get(CAP_SWITCH, {}).get("switch", {}).get("value") == "on"

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.coordinator.api.execute_command(self._device_id, CAP_SWITCH, "on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.coordinator.api.execute_command(self._device_id, CAP_SWITCH, "off")
        await self.coordinator.async_request_refresh()

