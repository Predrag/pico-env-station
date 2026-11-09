# pico-env-station

Environmental monitoring station built on **Raspberry Pi Pico W** with a DHT11 sensor, Wi-Fi connectivity, and a built-in web server. Sensor data is accessible via a browser dashboard, a REST API, and **Home Assistant**.

## Features

- Real-time temperature and humidity monitoring via DHT11
- Web dashboard (`/`) with links to memory stats
- REST API endpoints returning JSON
- Fully asynchronous operation (`asyncio`)
- Wi-Fi connection management with AP fallback mode
- Hardware button (GP15) to manually switch between STA and AP mode
- mDNS hostname (`pico.local`) in both STA and AP mode
- Built-in DNS server for AP mode (resolves all hostnames to Pico IP)
- Home Assistant integration (temperature & humidity visible in HA dashboard and mobile app)

## Hardware

| Component | Pin |
|-----------|-----|
| DHT11 DATA | GP16 |
| Button | GP15 |
| Onboard LED | "LED" |

## Project Structure

```
pico-env-station/
├── main.py                 # entry point
├── config.py               # credentials and pin config (not committed)
├── config.example.py       # template for config.py
├── server.py               # async HTTP server
├── wifi_manager.py         # Wi-Fi / AP management
├── dns_server.py           # DNS server for AP mode
├── sensors/
│   └── dht_sensor.py       # DHT11/DHT22 abstraction
├── libs/
│   ├── dht_led_asyncio.py
│   └── DIYables_MicroPython_LCD_I2C/
└── tests/                  # host-based pytest tests
```

## Setup

1. Clone the repository
2. Copy `config.example.py` to `config.py` and fill in your credentials:
   ```python
   SSID = "your_wifi_ssid"
   PASSWORD = "your_wifi_password"
   AP_SSID = "PicoEnvStation"
   AP_PASSWORD = "pico1234"
   AP_IP = "192.168.4.1"
   DHT_PIN = 16
   DHT_MODEL = 11
   BUTTON_PIN = 15
   SERVER_PORT = 80
   ```
3. Upload to Pico W using the **MicroPico** VS Code extension

## Wi-Fi Modes

| Mode | How to activate | Access URL |
|------|----------------|------------|
| STA (normal) | Automatic on boot | `http://pico.local` |
| AP (fallback) | Wi-Fi unavailable, or press button | `http://192.168.4.1` |

Press the button (GP15) at any time to toggle between modes.

## LED Status

| Blinks | Meaning |
|--------|---------|
| 1× | Boot |
| 2× | Connected to Wi-Fi |
| 3× | AP mode active |
| 5× | Wi-Fi failed during switch, staying in AP |

## API

| Endpoint | Description |
|----------|-------------|
| `GET /` | HTML dashboard |
| `GET /memory` | RAM usage page |
| `GET /api/temperature` | JSON: temperature, humidity |
| `GET /api/memory` | JSON: free/used/total RAM + % |

Example `/api/temperature` response:
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

## Home Assistant Integration

Pico sensor data is exposed to Home Assistant running on a **Raspberry Pi 4B**.

### Infrastructure

| Component | Runs on | Purpose |
|-----------|---------|---------|
| Home Assistant | Raspberry Pi 4B (Docker) | Reads Pico API, dashboards, automations |
| DuckDNS | Static record only (no updater) | Free DNS — static public IP, no auto-update needed |
| Caddy | Raspberry Pi 4B (systemd) | Reverse proxy with automatic HTTPS |

### Home Assistant setup (Docker on Raspberry Pi 4B)

```bash
mkdir -p ~/homeassistant
docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -v ~/homeassistant:/config \
  -e TZ=Europe/Bratislava \
  --network=host \
  ghcr.io/home-assistant/home-assistant:stable
```

Access at `http://localhost:8123` or `https://predrag-ha.duckdns.org`.

### configuration.yaml

```yaml
default_config:

homeassistant:
  external_url: "https://your-domain.duckdns.org"
  internal_url: "http://localhost:8123"

sensor:
  - platform: rest
    name: "Pico Teplota"
    unique_id: pico_temperature
    resource: http://<PICO_IP>/api/temperature
    value_template: "{{ value_json.temperature }}"
    unit_of_measurement: "°C"
    device_class: temperature
    scan_interval: 30

  - platform: rest
    name: "Pico Vlhkosť"
    unique_id: pico_humidity
    resource: http://<PICO_IP>/api/temperature
    value_template: "{{ value_json.humidity }}"
    unit_of_measurement: "%"
    device_class: humidity
    scan_interval: 30

http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 127.0.0.1
    - "::1"
    - "::ffff:127.0.0.1"
```

> **Note:** Use Pico's IP address instead of `pico.local` — mDNS does not work inside Docker containers.

> **Important:** If HA ignores `trusted_proxies` (logs: "not set-up for reverse proxies"), delete `~/homeassistant/.storage/http` and restart Docker container.

### Caddy (/etc/caddy/Caddyfile)

```
your-domain.duckdns.org {
    reverse_proxy 127.0.0.1:8123 {
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}
```

## Planned Features

- LCD I2C display integration
- Support for additional sensors
- Data logging

## Requirements

- MicroPython for Raspberry Pi Pico W
- VS Code + [MicroPico](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) extension
