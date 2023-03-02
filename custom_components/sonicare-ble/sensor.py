"""Support for Sonicare BLE sensors."""
from __future__ import annotations

from sonicare_bletb import SonicareSensor, SensorUpdate

from homeassistant import config_entries
from homeassistant.components.bluetooth.active_update_processor import (
    ActiveBluetoothProcessorCoordinator,
)
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothDataUpdate,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sensor import sensor_device_info_to_hass_device_info

from .const import DOMAIN
from .device import device_key_to_bluetooth_entity_key

import logging

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    SonicareSensor.BRUSHING_TIME: SensorEntityDescription(
        key=SonicareSensor.BRUSHING_TIME,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.SECONDS,
    ),
    SonicareSensor.HANDLE_TIME: SensorEntityDescription(
        key=SonicareSensor.HANDLE_TIME  # ,
        # device_class=SensorDeviceClass.TIMESTAMP,
        # state_class=SensorStateClass.,
        # native_unit_of_measurement=UnitOfTime.SECONDS,
    ),
    SonicareSensor.HANDLE_SESSION_STATE: SensorEntityDescription(
        key=SonicareSensor.HANDLE_SESSION_STATE
    ),
    SonicareSensor.SIGNAL_STRENGTH: SensorEntityDescription(
        key=SonicareSensor.SIGNAL_STRENGTH,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SonicareSensor.BATTERY_LEVEL: SensorEntityDescription(
        key=SonicareSensor.BATTERY_LEVEL,
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SonicareSensor.BRUSHING_SESSION_ID: SensorEntityDescription(
        key=SonicareSensor.BRUSHING_SESSION_ID
    ),
    SonicareSensor.LOADED_SESSION_ID: SensorEntityDescription(
        key=SonicareSensor.LOADED_SESSION_ID
    ),
    SonicareSensor.INTENSITY: SensorEntityDescription(key=SonicareSensor.INTENSITY),
    SonicareSensor.AVAILABLE_BRUSHING_ROUTINE: SensorEntityDescription(
        key=SonicareSensor.AVAILABLE_BRUSHING_ROUTINE
    ),
    SonicareSensor.ROUTINE_LENGTH: SensorEntityDescription(
        key=SonicareSensor.ROUTINE_LENGTH
    ),
}


def sensor_update_to_bluetooth_data_update(
    sensor_update: SensorUpdate,
) -> PassiveBluetoothDataUpdate:
    """Convert a sensor update to a bluetooth data update."""
    _LOGGER.debug(f"sensor_update_to_bluetooth_data_update: {sensor_update}")
    return PassiveBluetoothDataUpdate(
        devices={
            device_id: sensor_device_info_to_hass_device_info(device_info)
            for device_id, device_info in sensor_update.devices.items()
        },
        entity_descriptions={
            device_key_to_bluetooth_entity_key(device_key): SENSOR_DESCRIPTIONS[
                device_key.key
            ]
            for device_key in sensor_update.entity_descriptions
        },
        entity_data={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.native_value
            for device_key, sensor_values in sensor_update.entity_values.items()
        },
        entity_names={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.name
            for device_key, sensor_values in sensor_update.entity_values.items()
        },
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Sonicare BLE sensors."""
    _LOGGER.debug("SENSOR async_setup_entry")
    coordinator: ActiveBluetoothProcessorCoordinator = hass.data[DOMAIN][entry.entry_id]
    processor = PassiveBluetoothDataProcessor(sensor_update_to_bluetooth_data_update)
    entry.async_on_unload(
        processor.async_add_entities_listener(
            SonicareBluetoothSensorEntity, async_add_entities
        )
    )
    entry.async_on_unload(coordinator.async_register_processor(processor))


class SonicareBluetoothSensorEntity(
    PassiveBluetoothProcessorEntity[PassiveBluetoothDataProcessor[str | int | None]],
    SensorEntity,
):
    """Representation of a Sonicare sensor."""

    @property
    def native_value(self) -> str | int | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)
