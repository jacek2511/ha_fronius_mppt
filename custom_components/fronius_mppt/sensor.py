import logging
import async_timeout
from datetime import datetime, timedelta

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, CONF_IP_ADDRESS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    ip = config_entry.data[CONF_IP_ADDRESS]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, ip)},
        name=f"Fronius Inverter ({ip})",
        manufacturer="Fronius",
        model="Symo (Archive API)",
        configuration_url=f"http://{ip}",
    )

    entities = []
    
    sensors_config = [
        ("Voltage_DC_String_1", "Voltage DC S1", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE),
        ("Voltage_DC_String_2", "Voltage DC S2", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE),
        ("Current_DC_String_1", "Current DC S1", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT),
        ("Current_DC_String_2", "Current DC S2", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT),
        ("Temperature_Powerstage", "Inverter Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    ]

    for channel, name, unit, device_class in sensors_config:
        entities.append(FroniusArchiveSensor(coordinator, ip, channel, name, unit, device_class, device_info))

    entities.append(FroniusPowerSensor(coordinator, ip, 1, device_info))
    entities.append(FroniusPowerSensor(coordinator, ip, 2, device_info))

    async_add_entities(entities)

class FroniusDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, ip):
        super().__init__(
            hass,
            _LOGGER,
            name="Fronius MPPT Fetcher",
            update_interval=timedelta(seconds=300),
        )
        self.ip = ip

    async def _async_update_data(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        channels = [
            "Voltage_DC_String_1", "Voltage_DC_String_2",
            "Current_DC_String_1", "Current_DC_String_2",
            "Temperature_Powerstage"
        ]
        
        url = (f"http://{self.ip}/solar_api/v1/GetArchiveData.cgi?Scope=System"
               f"&StartDate={date_str}&EndDate={date_str}")
        for chan in channels:
            url += f"&Channel={chan}"

        try:
            session = async_get_clientsession(self.hass)
            
            async with async_timeout.timeout(15):
                async with session.get(url) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Inverter returned status {response.status}")
                    
                    res = await response.json(content_type=None)
                    
                    try:
                        data = res["Body"]["Data"]["inverter/1"]["Data"]
                    except (KeyError, TypeError):
                        _LOGGER.warning("Inverter connected but returned no data (it might be night)")
                        return {chan: 0 for chan in channels}

                    sample_channel = data.get("Voltage_DC_String_1", {}).get("Values", {})
                    if not sample_channel:
                        return {chan: 0 for chan in channels}
                    
                    latest_key = max(sample_channel.keys(), key=int)
                    
                    processed = {}
                    for chan in channels:
                        val = data.get(chan, {}).get("Values", {}).get(latest_key, 0)
                        processed[chan] = val
                    
                    return processed

        except Exception as err:
            raise UpdateFailed(f"Error communicating with Fronius: {err}")


class FroniusArchiveBaseEntity(CoordinatorEntity):
    def __init__(self, coordinator, device_info):
        super().__init__(coordinator)
        self._attr_device_info = device_info

class FroniusArchiveSensor(FroniusArchiveBaseEntity, SensorEntity):
    def __init__(self, coordinator, ip, channel, name, unit, device_class, device_info):
        super().__init__(coordinator, device_info)
        self._channel = channel
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT

        safe_ip = ip.replace(".", "_")
        safe_channel = channel.lower()
        self._attr_unique_id = f"fronius_{safe_channel}_{safe_ip}"      
        self.entity_id = f"sensor.fronius_{safe_channel}"

    @property
    def native_value(self):
        return self.coordinator.data.get(self._channel) if self.coordinator.data else None

class FroniusPowerSensor(FroniusArchiveBaseEntity, SensorEntity):
    def __init__(self, coordinator, ip, string_num, device_info):
        super().__init__(coordinator, device_info)
        self._string_num = string_num
        self._attr_name = f"Power DC S{string_num}"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        safe_ip = ip.replace(".", "_")
        self._attr_unique_id = f"fronius_p_s{string_num}_{safe_ip}"
        self.entity_id = f"sensor.fronius_power_dc_string_{string_num}"

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        v = self.coordinator.data.get(f"Voltage_DC_String_{self._string_num}")
        a = self.coordinator.data.get(f"Current_DC_String_{self._string_num}")
        return round(v * a, 2) if v is not None and a is not None else None
