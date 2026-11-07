# pico-env-station — kontext projektu

## Čo je tento projekt

Environmentálna monitorovacia stanica na **Raspberry Pi Pico W** s DHT11 senzorom, Wi-Fi pripojením a vstavaným webovým serverom. Napísaná v **MicroPython**.

## Stav projektu

Repozitár: https://github.com/Predrag/pico-env-station
- Vetva `main` — stabilné vydania
- Vetva `develop` — aktívny vývoj (default vetva na GitHub)

## Hardvér

| Komponent | Pin |
|-----------|-----|
| DHT11 DATA | GP16 |
| Onboard LED | "LED" |

## Štruktúra projektu

```
pico-env-station/
├── main.py                 # vstupný bod, asyncio loop
├── config.py               # Wi-Fi prihlasovacie údaje (NIE je v gite!)
├── config.example.py       # šablóna pre config.py
├── server.py               # asyncio HTTP server (port 80)
├── wifi_manager.py         # správa Wi-Fi pripojenia
├── sensors/
│   ├── __init__.py
│   └── dht_sensor.py       # abstrakcia pre DHT11/DHT22
├── libs/
│   ├── dht_led_asyncio.py              # starší standalone príklad
│   └── DIYables_MicroPython_LCD_I2C/  # LCD I2C knižnica (pripravená, ešte neintegrovaná)
├── tests/
│   ├── conftest.py          # mock-y MicroPython modulov (dht, machine, network)
│   ├── test_server.py       # 7 testov pre server.py
│   ├── test_dht_sensor.py   # 7 testov pre DHTSensor
│   └── test_wifi_manager.py # 5 testov pre WifiManager
├── pytest.ini               # asyncio_mode=auto, pythonpath=., testpaths=tests
├── README.md
└── .venv/                   # virtuálne prostredie (nie je v gite)
```

## API servera

| Endpoint | Popis |
|----------|-------|
| `GET /` | HTML dashboard, auto-refresh každých 5 sekúnd |
| `GET /api/temperature` | JSON: `{"temperature": 22, "humidity": 55, "unit": "celsius"}` |

## Testovanie

Testy bežia na PC bez akéhokoľvek hardvéru. MicroPython moduly (`dht`, `machine`, `network`) sú mockované v `tests/conftest.py`.

```bash
# spustenie testov
.venv/bin/pytest tests/ -v
```

19 testov, všetky prechádzajú.

## Upload na Pico W

Používa **MicroPico** rozšírenie pre VS Code. Konfigurácia v `.vscode/settings.json`.

Súbory ignorované pri uploade (`micropico.pyIgnore`):
`.claude`, `.vscode`, `.git`, `.gitignore`, `tests`, `.venv`, `pytest.ini`, `__pycache__`, `.pytest_cache`, `config.example.py`, `README.md`

## Dôležité poznámky

- `config.py` obsahuje reálne Wi-Fi heslo — **nikdy ho nekomitnúť**. Je v `.gitignore`.
- Na Pico ide: `main.py`, `config.py`, `server.py`, `wifi_manager.py`, `sensors/`, `libs/`
- LCD knižnica (`DIYables_MicroPython_LCD_I2C`) je v projekte, ale ešte nie je integrovaná do `main.py`

## Plánované rozšírenia

- Integrácia LCD I2C displeja
- Podpora ďalších senzorov
- Logovanie dát
