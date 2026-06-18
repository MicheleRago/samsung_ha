import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_ACCESS_TOKEN, CONF_REFRESH_TOKEN
from .api import SmartThingsApi
from .coordinator import SmartThingsCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "switch", "select", "button", "binary_sensor", "number", "light"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Samsung Custom Appliances from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client_id = entry.data.get(CONF_CLIENT_ID)
    client_secret = entry.data.get(CONF_CLIENT_SECRET)
    access_token = entry.data.get(CONF_ACCESS_TOKEN)
    refresh_token = entry.data.get(CONF_REFRESH_TOKEN)

    async def save_tokens(new_access, new_refresh):
        new_data = {**entry.data}
        new_data[CONF_ACCESS_TOKEN] = new_access
        new_data[CONF_REFRESH_TOKEN] = new_refresh
        hass.config_entries.async_update_entry(entry, data=new_data)

    api = SmartThingsApi(client_id, client_secret, access_token, refresh_token, save_tokens)
    coordinator = SmartThingsCoordinator(hass, api)

    await coordinator.async_init()
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
