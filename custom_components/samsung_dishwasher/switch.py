import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CAP_SWITCH

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DishwasherPowerSwitch(coordinator)])

class DishwasherPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for power."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.api.device_id}_power"
        self._attr_name = "Power"
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.api.device_id)},
            "name": "Samsung Dishwasher",
            "manufacturer": "Samsung",
        }

    @property
    def is_on(self):
        """Return true if switch is on."""
        data = self.coordinator.data
        if not data:
            return False
        return data.get(CAP_SWITCH, {}).get("switch", {}).get("value") == "on"

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.coordinator.api.execute_command(CAP_SWITCH, "on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.coordinator.api.execute_command(CAP_SWITCH, "off")
        await self.coordinator.async_request_refresh()
