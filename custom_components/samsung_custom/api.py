import aiohttp
import logging
from typing import Any, Dict, List

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.smartthings.com/v1"

class SmartThingsApi:
    """API wrapper for SmartThings."""

    def __init__(self, pat: str):
        """Initialize the API."""
        self.pat = pat
        self.headers = {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json"
        }

    async def get_devices(self) -> List[Dict[str, Any]]:
        """Get list of all devices."""
        url = f"{BASE_URL}/devices"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("items", [])

    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get the full status of the device."""
        url = f"{BASE_URL}/devices/{device_id}/status"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                data = await response.json()
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
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload) as response:
                response.raise_for_status()
                _LOGGER.debug(f"Command executed successfully: {component}.{capability}.{command}({arguments})")
