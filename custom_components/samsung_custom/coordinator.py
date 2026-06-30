"""Data update coordinator for Samsung Custom Appliances."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SmartThingsApi
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class SmartThingsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, api: SmartThingsApi):
        """Initialize."""
        self.api = api
        self.devices = []
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def async_init(self) -> None:
        """Fetch devices before first update."""
        self.devices = await self.api.get_devices()

    async def _async_update_data(self) -> dict:
        """Update data via API."""
        try:
            data = {}
            for device in self.devices:
                device_id = device.get("deviceId")
                if device_id:
                    status = await self.api.get_device_status(device_id)
                    data[device_id] = {
                        "device_info": device,
                        "status": status,
                    }
            return data
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception
