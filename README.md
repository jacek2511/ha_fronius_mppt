# Fronius MPPT Archive Integration for Home Assistant
This custom component extracts high-resolution string-level data (Voltage, Current, Power, and Temperature) from Fronius Symo/Primo inverters using the GetArchiveData.cgi API. Unlike the standard integration, this specifically targets the MPPT trackers' archive data, which is useful for detailed string performance monitoring.

**Features**
* Real-time Archival Polling: Fetches the latest data points from the inverter's internal logger.
* Dual String Monitoring: Provides independent Voltage, Current, and Power sensors for both String 1 and String 2.
* Efficiency: Uses DataUpdateCoordinator to fetch all data in a single HTTP request every 5 minutes.
* Fully Configurable: Easy setup via the Home Assistant Integration UI (Config Flow).
* Device Registry: All sensors are neatly grouped under one "Fronius Inverter" device.

**Sensors Provided**
```
Sensor Name         Unit   Description
Voltage DC S1/S2    V      Input voltage for each MPPT tracker
Current DC S1/S2    A      Input current for each MPPT tracker
Power DC S1/S2      W      Calculated power ($P = U \times I$) per stringInverter 
Temperature        °C      Internal temperature of the power stage
```
# Installation
### Manual Installation
Copy the fronius_mppt folder into your Home Assistant custom_components directory.

The structure should look like this:

```
config/custom_components/fronius_mppt/
├── __init__.py
├── config_flow.py
├── const.py
├── manifest.json
└── sensor.py
```
Restart Home Assistant.

### Configuration
Go to Settings -> Devices & Services.

Click Add Integration.

Search for Fronius MPPT Archiver.

Enter the IP Address of your Fronius Datamanager (e.g., 192.168.1.100).

Submit. Your sensors will appear shortly.

**Important Notes**
* Polling Interval: This integration polls every 5 minutes (300 seconds) to match the internal logging frequency of the Fronius Datamanager.
* Night Time: During the night, the Archive API may return empty values. The integration handles this by displaying 0 or Unknown until production resumes in the morning.
* Local API: Ensure that the "Solar API" is enabled in your Fronius Web Interface under Settings -> Datalogger -> Solar API.

**Troubleshooting**
If you encounter a Mimetype error (text/javascript), ensure you are using the latest version of this integration which bypasses strict content-type checking. For other errors, check your Home Assistant logs under Settings -> System -> Logs.  
