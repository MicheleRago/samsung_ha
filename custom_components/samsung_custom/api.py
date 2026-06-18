import logging
import aiohttp
from typing import Any, Dict

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.smartthings.com/v1"
OAUTH_TOKEN_URL = "https://api.smartthings.com/oauth/token"

class SmartThingsApi:
    """Class to interact with the SmartThings API."""

    def __init__(self, client_id: str, client_secret: str, access_token: str, refresh_token: str, save_tokens_callback=None):
        """Initialize the API client."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.save_tokens_callback = save_tokens_callback

    @property
    def headers(self) -> Dict[str, str]:
        """Return the headers for API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def async_refresh_token_if_needed(self) -> None:
        """Check token validity or forcefully refresh it.
        SmartThings API will return 401 if expired. We will handle the 401 directly in the methods.
        """
        pass # The refresh happens gracefully on 401

    async def _do_refresh_token(self) -> None:
        """Perform the actual token refresh."""
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.refresh_token
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(OAUTH_TOKEN_URL, data=payload, headers=headers, auth=auth) as response:
                response.raise_for_status()
                data = await response.json()
                
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                
                if self.save_tokens_callback:
                    await self.save_tokens_callback(self.access_token, self.refresh_token)
                
                _LOGGER.debug("SmartThings OAuth tokens refreshed successfully.")

    async def _request(self, method: str, url: str, **kwargs) -> Any:
        """Make an API request and handle token refresh on 401."""
        async with aiohttp.ClientSession() as session:
            kwargs["headers"] = self.headers
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    _LOGGER.info("Access token expired. Refreshing token...")
                    await self._do_refresh_token()
                    kwargs["headers"] = self.headers
                    async with session.request(method, url, **kwargs) as retry_response:
                        retry_response.raise_for_status()
                        return await retry_response.json()
                
                if response.status >= 400:
                    text = await response.text()
                    _LOGGER.error(f"API Error {response.status}: {text}")
                response.raise_for_status()
                if response.status == 204:
                    return None
                return await response.json()

    async def get_devices(self) -> list:
        """Get all devices."""
        url = f"{BASE_URL}/devices"
        data = await self._request("GET", url)
        return data.get("items", [])

    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get the full status of the device."""
        url = f"{BASE_URL}/devices/{device_id}/status"
        data = await self._request("GET", url)
        return data.get("components", {})

    async def execute_command(self, device_id: str, component: str, capability: str, command: str, arguments: list = None) -> None:
        """Execute a command on the device."""
        url = f"{BASE_URL}/devices/{device_id}/commands"
        
        payload = {
            "commands": [
                {
                    "component": component,
                    "capability": capability,
                    "command": command,
                    "arguments": arguments or []
                }
            ]
        }
        
        await self._request("POST", url, json=payload)
        _LOGGER.debug(f"Command executed successfully: {component}.{capability}.{command}({arguments})")
