# pico-env-station

Environmental monitoring station built on **Raspberry Pi Pico W** with a DHT11 sensor, Wi-Fi connectivity, and a built-in web server. Sensor data is accessible via a browser dashboard and a REST API.

## Features

- Real-time temperature and humidity monitoring via DHT11
- Web dashboard with auto-refresh (every 5 seconds)
- REST API endpoint returning JSON
- Fully asynchronous operation (`asyncio`)
- Wi-Fi connection management

## Hardware

| Component | Pin |
|-----------|-----|
| DHT11 DATA | GP16 |

## Project Structure

```
pico-env-station/
├── main.py                 # entry point
├── config.py               # Wi-Fi credentials (not committed)
├── config.example.py       # template for config.py
├── server.py               # async HTTP server
├── wifi_manager.py         # Wi-Fi connection management
├── sensors/
│   └── dht_sensor.py       # DHT11/DHT22 abstraction
├── libs/
│   ├── dht_led_asyncio.py
│   └── DIYables_MicroPython_LCD_I2C/
└── tests/                  # host-based pytest tests
```

## Setup

1. Clone the repository
2. Copy `config.example.py` to `config.py` and fill in your Wi-Fi credentials:
   ```python
   SSID = "your_wifi_ssid"
   PASSWORD = "your_wifi_password"
   ```
3. Upload to Pico W using the **MicroPico** VS Code extension

## API

| Endpoint | Description |
|----------|-------------|
| `GET /` | HTML dashboard |
| `GET /api/temperature` | JSON sensor data |

Example JSON response:
```json
{
  "temperature": 22,
  "humidity": 55,
  "unit": "celsius"
}
```

## Development & Testing

Tests run on a PC without any hardware:

```bash
python -m venv .venv
source .venv/bin/activate
pip install pytest pytest-asyncio
pytest tests/ -v
```

## Planned Features

- LCD I2C display integration
- Support for additional sensors
- Data logging

## Requirements

- MicroPython for Raspberry Pi Pico W
- VS Code + [MicroPico](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) extension
