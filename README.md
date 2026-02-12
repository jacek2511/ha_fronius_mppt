[![GitHub Latest Release][releases_shield]][releases] ![Downloads][downloads] [![License][license-shield]](LICENSE) [![GH-last-commit][latest_commit]][commits] [![HACS][hacsbadge]][hacs] [![Stars][stars]]()

[releases_shield]: https://img.shields.io/github/release/jacek2511/ha_fronius_mppt.svg
[releases]: https://github.com/jacek2511/ha_fronius_mppt/releases/latest
[downloads]: https://img.shields.io/github/downloads/jacek2511/ha_fronius_mppt/total
[license-shield]: https://img.shields.io/github/license/jacek2511/ha_fronius_mppt
[latest_commit]: https://img.shields.io/github/last-commit/jacek2511/ha_fronius_mppt.svg
[commits]: https://github.com/jack2511/ha_fronius_mppt/commits/master
[stars]: https://img.shields.io/github/stars/jacek2511/ha_fronius_mppt?style=flat
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg


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

📊 Example ApexCharts Visualization, use the following code:
```
type: custom:apexcharts-card
graph_span: 24h
header:
  show: true
  title: Solar Strings DC Power (W)
  show_states: true
  colorize_states: true
series:
  - entity: sensor.fronius_power_dc_string_1
    name: String 1
    type: area
    color: "#ff9800"
    opacity: 0.3
    stroke_width: 2
    group_by:
      func: last
      duration: 5m
  - entity: sensor.fronius_power_dc_string_2
    name: String 2
    type: area
    color: "#2196f3"
    opacity: 0.3
    stroke_width: 2
    group_by:
      func: last
      duration: 5m
```
💻 Example dashboard code:
```
type: vertical-stack
cards:
  - graph: line
    type: sensor
    entity: sensor.fronius_temperature_powerstage
    name: Inverter Temperature
    detail: 1
  - type: grid
    title: String Performance Comparison
    columns: 2
    square: false
    cards:
      - type: entities
        title: MPPT String 1
        entities:
          - entity: sensor.fronius_power_dc_string_1
            name: Power
          - entity: sensor.fronius_voltage_dc_string_1
            name: Voltage
          - entity: sensor.fronius_current_dc_string_1
            name: Current
      - type: entities
        title: MPPT String 2
        entities:
          - entity: sensor.fronius_power_dc_string_2
            name: Power
          - entity: sensor.fronius_voltage_dc_string_2
            name: Voltage
          - entity: sensor.fronius_current_dc_string_2
            name: Current
  - type: history-graph
    title: Power Output History (Watts)
    entities:
      - entity: sensor.fronius_power_dc_string_1
        name: String 1
      - entity: sensor.fronius_power_dc_string_2
        name: String 2
    hours_to_show: 24
    refresh_interval: 300
```

**Important Notes**
* Polling Interval: This integration polls every 5 minutes (300 seconds) to match the internal logging frequency of the Fronius Datamanager.
* Night Time: During the night, the Archive API may return empty values. The integration handles this by displaying 0 or Unknown until production resumes in the morning.
* Local API: Ensure that the "Solar API" is enabled in your Fronius Web Interface under Settings -> Datalogger -> Solar API.

**Troubleshooting**
If you encounter a Mimetype error (text/javascript), ensure you are using the latest version of this integration which bypasses strict content-type checking. For other errors, check your Home Assistant logs under Settings -> System -> Logs.  
