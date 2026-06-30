from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SmartThingsApi
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_REFRESH_TOKEN,
    DOMAIN,
)
from .coordinator import SmartThingsCoordinator

PLATFORMS = ("sensor", "switch", "select", "button", "binary_sensor", "number", "light")


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

    session = async_get_clientsession(hass)
    api = SmartThingsApi(
        client_id,
        client_secret,
        access_token,
        refresh_token,
        session,
        save_tokens,
    )
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
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
