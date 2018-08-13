from hbmqtt.plugins.authentication import BaseAuthPlugin


class HassAuthPlugin(BaseAuthPlugin):
    def __init__(self, context):
        super().__init__(context)
        try:
            self.hass = self.auth_config['home-assistant']
        except KeyError:
            self.context.logger.warning("'home-assistant' key not found in auth configuration")

    async def authenticate(self, *args, **kwargs):
        authenticated = super().authenticate(*args, **kwargs)

        if not authenticated:
            return authenticated

        session = kwargs.get('session', None)

        if (session is None or
                session.username is None or
                session.password is None):
            return False

        # Backwards compat
        if session.username == 'homeassistant':
            legacy_prov = _find_provider(self.hass, 'legacy_api_password')

            try:
                legacy_prov.async_validate_login(session.password)
                return True
            except Exception:
                pass

        hass_prov = _find_provider(self.hass, 'homeassistant')

        await hass_prov.async_initialize()

        try:
            await hass_prov.async_validate_login(
                session.username, session.password)
            print("AUTHENTICATED", session.username)
            return True
        except Exception:
            return False


def _find_provider(hass, prov_type):
    """Return provider for type."""
    for provider in hass.auth.auth_providers:
        if provider.type == prov_type:
            return provider
    return None
