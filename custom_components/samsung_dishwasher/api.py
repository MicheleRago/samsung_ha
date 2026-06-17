import aiohttp
import logging
from typing import Any, Dict

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.smartthings.com/v1"

class SmartThingsApi:
    """API wrapper for SmartThings."""

    def __init__(self, pat: str, device_id: str):
        """Initialize the API."""
        self.pat = pat
        self.device_id = device_id
        self.headers = {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json"
        }

    async def get_device_status(self) -> Dict[str, Any]:
        """Get the full status of the device."""
        url = f"{BASE_URL}/devices/{self.device_id}/status"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("components", {}).get("main", {})

    async def execute_command(self, capability: str, command: str, arguments: list = None) -> None:
        """Execute a command on the device."""
        url = f"{BASE_URL}/devices/{self.device_id}/commands"
        
        payload = {
            "commands": [
                {
                    "component": "main",
                    "capability": capability,
                    "command": command,
                    "arguments": arguments or []
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload) as response:
                response.raise_for_status()
                _LOGGER.debug(f"Command executed successfully: {capability}.{command}({arguments})")
