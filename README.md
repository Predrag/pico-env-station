# pico-env-station

Environmental monitoring station built on **Raspberry Pi Pico W** with a DHT11 sensor, Wi-Fi connectivity, and a built-in web server. Sensor data is accessible via a browser dashboard, a REST API, and **Google Home / Google Assistant**.

## Features

- Real-time temperature and humidity monitoring via DHT11
- Web dashboard (`/`) with links to memory stats
- REST API endpoints returning JSON
- Fully asynchronous operation (`asyncio`)
- Wi-Fi connection management with AP fallback mode
- Hardware button (GP15) to manually switch between STA and AP mode
- mDNS hostname (`pico.local`) in both STA and AP mode
- Built-in DNS server for AP mode (resolves all hostnames to Pico IP)
- Google Home / Google Assistant integration via Home Assistant

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

## Google Home Integration

Pico sensor data is exposed to Google Home via **Home Assistant**.

### Infrastructure required

| Component | Purpose |
|-----------|---------|
| Home Assistant (Podman) | Reads Pico API, exposes to Google |
| DuckDNS | Free dynamic DNS (`predrag-ha.duckdns.org`) |
| Caddy | Reverse proxy with automatic HTTPS (Let's Encrypt) |
| Google Actions project | Links Google Home to Home Assistant |

### Home Assistant setup (Podman)

```bash
mkdir -p ~/homeassistant
podman run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -v ~/homeassistant:/config:Z \
  -e TZ=Europe/Bratislava \
  --network=host \
  ghcr.io/home-assistant/home-assistant:stable
```

Access at `http://localhost:8123`.

### configuration.yaml (~/homeassistant/configuration.yaml)

```yaml
homeassistant:
  external_url: "https://your-domain.duckdns.org"
  internal_url: "http://localhost:8123"

sensor:
  - platform: rest
    name: "Pico Teplota"
    unique_id: pico_temperature
    resource: http://pico.local/api/temperature
    value_template: "{{ value_json.temperature }}"
    unit_of_measurement: "°C"
    device_class: temperature
    scan_interval: 30

  - platform: rest
    name: "Pico Vlhkosť"
    unique_id: pico_humidity
    resource: http://pico.local/api/temperature
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

google_assistant:
  project_id: YOUR_GOOGLE_ACTIONS_PROJECT_ID
  service_account: !include SERVICE_ACCOUNT.json
  report_state: true
  exposed_domains:
    - sensor
```

> **Important:** If Home Assistant ignores `trusted_proxies` (error in logs: "not set-up for reverse proxies"), delete `~/.homeassistant/.storage/http` and restart. This forces HA to reload the HTTP config from YAML.

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

### Google Actions setup

1. Create project at [console.home.google.com](https://console.home.google.com)
2. Cloud-to-cloud → Develop → Add integration
3. Fill in OAuth fields:
   - **OAuth Client ID:** `https://oauth-redirect.googleusercontent.com/r/YOUR_PROJECT_ID`
   - **Client secret:** `homeassistant`
   - **Authorization URL:** `https://your-domain.duckdns.org/auth/authorize`
   - **Token URL:** `https://your-domain.duckdns.org/auth/token`
4. Enable **HomeGraph API** in Google Cloud Console
5. Create a **Service Account** (role: Service Account Token Creator), download JSON key → save as `~/homeassistant/SERVICE_ACCOUNT.json`
6. In Google Home app: **+ → Set up device → Works with Google** → find your integration → log in

### Voice commands

- *"Hey Google, what is the temperature?"*
- *"Hey Google, what is the humidity?"*

## Planned Features

- LCD I2C display integration
- Support for additional sensors
- Data logging

## Requirements

- MicroPython for Raspberry Pi Pico W
- VS Code + [MicroPico](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) extension
