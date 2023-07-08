"""Data coordinator for receiving SonicareBLETB updates."""

import logging

from sonicare_bletb import SonicareBLETB, SonicareBLETBState

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SonicareBLETBCoordinator(DataUpdateCoordinator[None]):
    """Data coordinator for receiving SonicareBLETB updates."""

    def __init__(self, hass: HomeAssistant, sonicare_ble: SonicareBLETB) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )
        self._sonicare_ble = sonicare_ble
        sonicare_ble.register_callback(self._async_handle_update)
        sonicare_ble.register_disconnected_callback(self._async_handle_disconnect)
        self.connected = True

    @callback
    def _async_handle_update(self, state: SonicareBLETBState) -> None:
        """Just trigger the callbacks."""
        _LOGGER.warning("_async_handle_update")
        self.connected = True
        self.async_set_updated_data(None)

    @callback
    def _async_handle_disconnect(self) -> None:
        """Trigger the callbacks for disconnected."""
        _LOGGER.warning("_async_handle_disconnect")
        self.connected = False
        self.async_update_listeners()
