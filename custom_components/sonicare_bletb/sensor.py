"""Sonicare BLE toothbrush integration sensor platform."""


from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SonicareBLETB, SonicareBLETBCoordinator
from .const import DOMAIN
from .models import SonicareBLETBData

BRUSHING_TIME_DESCRIPTION = SensorEntityDescription(
    key="brushing_time",
    device_class=SensorDeviceClass.DURATION,
    entity_registry_enabled_default=True,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Brushing time",
    native_unit_of_measurement=UnitOfTime.SECONDS,
    state_class=SensorStateClass.MEASUREMENT,
)

BATTERY_LEVEL_DESCRIPTION = SensorEntityDescription(
    key="battery_level",
    device_class=SensorDeviceClass.BATTERY,
    entity_registry_enabled_default=True,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Battery level",
    native_unit_of_measurement=PERCENTAGE,
    state_class=SensorStateClass.MEASUREMENT,
)

ROUTINE_LENGTH_DESCRIPTION = SensorEntityDescription(
    key="routine_length",
    device_class=SensorDeviceClass.DURATION,
    entity_registry_enabled_default=True,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Routine length",
    native_unit_of_measurement=UnitOfTime.SECONDS,
    state_class=SensorStateClass.MEASUREMENT,
)

HANDLE_STATE_DESCRIPTION = SensorEntityDescription(
    key="handle_state",
    device_class=None,
    entity_registry_enabled_default=True,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Handle state",
    # native_unit_of_measurement="",
    # state_class=SensorStateClass.,
)

AVAILABLE_BRUSHING_ROUTINE_DESCRIPTION = SensorEntityDescription(
    key="available_brushing_routine",
    device_class=None,
    entity_registry_enabled_default=True,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Available brushing routine",
    # native_unit_of_measurement="Target Energy",
    # state_class=SensorStateClass.MEASUREMENT,
)

INTENSITY_DESCRIPTION = SensorEntityDescription(
    key="intensity",
    entity_registry_enabled_default=True,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Intensity",
    # native_unit_of_measurement="Gates",
)

LOADED_SESSION_ID_DESCRIPTION = SensorEntityDescription(
    key="loaded_session_id",
    entity_registry_enabled_default=True,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Loaded session id",
)

HANDLE_TIME_DESCRIPTION = SensorEntityDescription(
    key="handle_time",
    entity_registry_enabled_default=True,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Handle time",
)

BRUSHING_SESSION_ID_DESCRIPTION = SensorEntityDescription(
    key="brushing_session_id",
    entity_registry_enabled_default=True,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Brushing session id",
)

LAST_SESSION_ID_DESCRIPTION = SensorEntityDescription(
    key="last_session_id",
    entity_registry_enabled_default=True,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Last session id",
)


SENSOR_DESCRIPTIONS = [
    BRUSHING_TIME_DESCRIPTION,
    BATTERY_LEVEL_DESCRIPTION,
    ROUTINE_LENGTH_DESCRIPTION,
    HANDLE_STATE_DESCRIPTION,
    AVAILABLE_BRUSHING_ROUTINE_DESCRIPTION,
    INTENSITY_DESCRIPTION,
    LOADED_SESSION_ID_DESCRIPTION,
    HANDLE_TIME_DESCRIPTION,
    BRUSHING_SESSION_ID_DESCRIPTION,
    LAST_SESSION_ID_DESCRIPTION,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform for SonicareBLETB."""
    data: SonicareBLETBData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SonicareBLETBSensor(
            data.coordinator,
            data.device,
            entry.title,
            description,
        )
        for description in SENSOR_DESCRIPTIONS
    )


class SonicareBLETBSensor(CoordinatorEntity[SonicareBLETBCoordinator], SensorEntity, RestoreEntity):
    """Generic sensor for SonicareBLETB."""

    def __init__(
        self,
        coordinator: SonicareBLETBCoordinator,
        device: SonicareBLETB,
        name: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._device = device
        self._key = description.key
        self.entity_description = description
        self._attr_unique_id = f"{device.address}_{self._key}"
        self._attr_device_info = DeviceInfo(
            name=name,
            connections={(dr.CONNECTION_BLUETOOTH, device.address)},
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if not(last_state := await self.async_get_last_state()):
            return
        self._attr_native_value = last_state.state

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = getattr(self._device, self._key)
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Unavailable if coordinator isn't connected."""
        return True

    @property
    def assumed_state(self) -> bool:
        return not self._coordinator.connected

    @property
    def native_value(self) -> str | int | None:
        return getattr(self._device, self._key)
