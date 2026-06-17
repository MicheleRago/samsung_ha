import logging
import voluptuous as vol
import aiohttp
import urllib.parse
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_ACCESS_TOKEN, CONF_REFRESH_TOKEN

_LOGGER = logging.getLogger(__name__)

OAUTH_AUTH_URL = "https://api.smartthings.com/oauth/authorize"
OAUTH_TOKEN_URL = "https://api.smartthings.com/oauth/token"
REDIRECT_URI = "https://google.com"

class SmartThingsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Samsung Custom Appliances."""

    VERSION = 2

    def __init__(self):
        """Initialize."""
        self.client_id = None
        self.client_secret = None

    async def async_step_user(self, user_input=None):
        """Step 1: Ask for Client ID and Secret."""
        errors = {}
        if user_input is not None:
            self.client_id = user_input[CONF_CLIENT_ID]
            self.client_secret = user_input[CONF_CLIENT_SECRET]
            return await self.async_step_auth()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_CLIENT_ID): str,
                vol.Required(CONF_CLIENT_SECRET): str,
            }),
            errors=errors,
            description_placeholders={
                "instructions": "Inserisci il Client ID e il Client Secret del tuo progetto SmartThings."
            }
        )

    async def async_step_auth(self, user_input=None):
        """Step 2: Provide Auth URL and ask for Auth Code."""
        errors = {}
        
        if user_input is not None:
            auth_url_pasted = user_input.get("auth_url")
            try:
                parsed_url = urllib.parse.urlparse(auth_url_pasted)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                auth_code = query_params.get("code", [None])[0]
                
                redirect_uri_used = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                # Forza il redirect_uri corretto se Google ha aggiunto www. o la barra finale
                if "google.com" in redirect_uri_used:
                    redirect_uri_used = REDIRECT_URI
                
                if not auth_code:
                    errors["base"] = "invalid_code"
                else:
                    return await self._exchange_code_for_token(auth_code, redirect_uri_used)
            except Exception:
                errors["base"] = "invalid_url"

        safe_client_id = urllib.parse.quote(self.client_id)
        safe_redirect_uri = urllib.parse.quote(REDIRECT_URI)
        auth_link = f"{OAUTH_AUTH_URL}?client_id={safe_client_id}&response_type=code&redirect_uri={safe_redirect_uri}&scope=r:devices:* x:devices:*"

        return self.async_show_form(
            step_id="auth",
            data_schema=vol.Schema({
                vol.Required("auth_url"): str,
            }),
            errors=errors,
            description_placeholders={
                "auth_link": auth_link
            }
        )

    async def _exchange_code_for_token(self, auth_code: str, redirect_uri: str):
        """Exchange the auth code for access and refresh tokens."""
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "redirect_uri": redirect_uri
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(OAUTH_TOKEN_URL, data=payload, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    access_token = data.get("access_token")
                    refresh_token = data.get("refresh_token")
                    
                    if not access_token or not refresh_token:
                        return self.async_abort(reason="missing_tokens")
                        
                    return self.async_create_entry(
                        title="Samsung Custom Appliances",
                        data={
                            CONF_CLIENT_ID: self.client_id,
                            CONF_CLIENT_SECRET: self.client_secret,
                            CONF_ACCESS_TOKEN: access_token,
                            CONF_REFRESH_TOKEN: refresh_token,
                        }
                    )
        except Exception as e:
            _LOGGER.error("Error exchanging code for token: %s", e)
            return self.async_abort(reason="oauth_error")
