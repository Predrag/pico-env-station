# pico-env-station — kontext projektu

## Čo je tento projekt

Environmentálna monitorovacia stanica na **Raspberry Pi Pico W** s DHT11 senzorom, Wi-Fi pripojením, vstavaným webovým serverom a integráciou s **Home Assistant**. Napísaná v **MicroPython**.

## Stav projektu

Repozitár: https://github.com/Predrag/pico-env-station
- Vetva `main` — stabilné vydania
- Vetva `develop` — aktívny vývoj (default vetva na GitHub)

## Hardvér

| Komponent | Pin |
|-----------|-----|
| DHT11 DATA | GP16 |
| Tlačidlo (prepínanie režimov) | GP15 |
| Onboard LED | "LED" |

## Štruktúra projektu

```
pico-env-station/
├── main.py                 # vstupný bod, asyncio loop
├── config.py               # prihlasovacie údaje a piny (NIE je v gite!)
├── config.example.py       # šablóna pre config.py
├── server.py               # asyncio HTTP server (port 80)
├── wifi_manager.py         # správa Wi-Fi / AP režimu
├── dns_server.py           # DNS server pre AP režim
├── sensors/
│   ├── __init__.py
│   └── dht_sensor.py       # abstrakcia pre DHT11/DHT22
├── libs/
│   ├── dht_led_asyncio.py              # starší standalone príklad
│   └── DIYables_MicroPython_LCD_I2C/  # LCD I2C knižnica (pripravená, ešte neintegrovaná)
├── tests/
│   ├── conftest.py          # mock-y MicroPython modulov (dht, machine, network, gc)
│   ├── test_server.py       # testy pre server.py
│   ├── test_dht_sensor.py   # testy pre DHTSensor
│   └── test_wifi_manager.py # testy pre WifiManager
├── pytest.ini               # asyncio_mode=auto, pythonpath=., testpaths=tests
├── README.md
└── .venv/                   # virtuálne prostredie (nie je v gite)
```

## API servera

| Endpoint | Popis |
|----------|-------|
| `GET /` | HTML dashboard s odkazom na /memory |
| `GET /memory` | HTML stránka využitia RAM |
| `GET /api/temperature` | JSON: teplota, vlhkosť |
| `GET /api/memory` | JSON: free_b, used_b, total_b, used_pct |

## Wi-Fi režimy

- **STA** (normal): Pico sa pripojí na WiFi, dostupný na `http://pico.local`
- **AP** (fallback): Pico vytvorí hotspot `PicoEnvStation`, dostupný na `http://192.168.4.1`
- Tlačidlo GP15 prepína medzi režimami za behu
- DNS server (`dns_server.py`) v AP režime vracia IP Pica pre akýkoľvek hostname

## Testovanie

Testy bežia na PC bez akéhokoľvek hardvéru. MicroPython moduly (`dht`, `machine`, `network`) a `gc.mem_free`/`gc.mem_alloc` sú mockované v `tests/conftest.py`.

```bash
.venv/bin/pytest tests/ -v
```

## Upload na Pico W

Používa **MicroPico** rozšírenie pre VS Code. Konfigurácia v `.vscode/settings.json`.

Súbory ignorované pri uploade (`micropico.pyIgnore`):
`.claude`, `.vscode`, `.git`, `.gitignore`, `tests`, `.venv`, `pytest.ini`, `__pycache__`, `.pytest_cache`, `config.example.py`, `README.md`, `CLAUDE.md`, `.micropico`

## Dôležité poznámky

- `config.py` obsahuje reálne Wi-Fi heslo — **nikdy ho nekomitnúť**. Je v `.gitignore`.
- Na Pico ide: `main.py`, `config.py`, `server.py`, `wifi_manager.py`, `dns_server.py`, `sensors/`, `libs/`
- LCD knižnica (`DIYables_MicroPython_LCD_I2C`) je v projekte, ale ešte nie je integrovaná do `main.py`
- `pico.local` mDNS nefunguje v Docker kontajneri — v HA konfigurácii používaj IP adresu Pica (`192.168.0.235`)

## Home Assistant integrácia

### Infraštruktúra (beží na Raspberry Pi 4B — autonómne, nezávislé od Fedory)

| Komponent | Umiestnenie | Popis |
|-----------|-------------|-------|
| Home Assistant | Docker kontajner na Pi 4B | čita `/api/temperature` z Pica |
| DuckDNS | statický DNS záznam (bez timera) | `predrag-ha.duckdns.org` → `88.212.33.47` (statická IP, nepotrebuje aktualizácie) |
| Caddy | systemd služba na Pi 4B | reverse proxy s HTTPS (Let's Encrypt) |

SSH prístup na Pi: `ssh -i ~/.ssh/githubSsh rpi4@rpi4.local`
Pi IP adresa: `192.168.0.89`

### Správa Home Assistant (cez SSH na Pi)

```bash
ssh -i ~/.ssh/githubSsh rpi4@rpi4.local

docker start homeassistant    # spustiť
docker stop homeassistant     # zastaviť
docker restart homeassistant  # reštartovať
docker logs homeassistant     # logy
```

Konfigurácia: `~/homeassistant/configuration.yaml` (na Pi)
Dashboard: `~/homeassistant/ui-lovelace.yaml` a `~/homeassistant/pico-dashboard.yaml`

### Kritická poznámka — trusted_proxies

V HA 2024+ je HTTP konfigurácia migrovaná do `.storage/http` a YAML sa ignoruje.
Ak HA hlási `"not set-up for reverse proxies"` napriek správnemu YAML:

```bash
ssh -i ~/.ssh/githubSsh rpi4@rpi4.local
docker exec homeassistant rm -f /config/.storage/http
docker restart homeassistant
```

### DuckDNS

Statický záznam — `predrag-ha.duckdns.org` trvalo smeruje na `88.212.33.47`.
DuckDNS timer bol odstránený (statická IP sa nemení, aktualizácie nie sú potrebné).

### Caddy (na Pi)

```bash
ssh -i ~/.ssh/githubSsh rpi4@rpi4.local
sudo systemctl status caddy
sudo systemctl reload caddy
```

Caddyfile: `/etc/caddy/Caddyfile` — proxy na `127.0.0.1:8123`
Externá URL: `https://predrag-ha.duckdns.org`

## Plánované rozšírenia

- Integrácia LCD I2C displeja
- Podpora ďalších senzorov
- Logovanie dát
