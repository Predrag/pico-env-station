SSID = "your_wifi_ssid"
PASSWORD = "your_wifi_password"

# Domáca sieť — BSSID prehľad (Pico W podporuje len 2.4GHz)
# Siet (2.4GHz):
#   RT-AX86U (hlavný router): 3C:7C:3F:6B:A4:E0
#   RP-BE58  (repeater, obývačka): 8A:AD:9F:E4:C8:C9  ← Pico sa pripája sem
# Siet 5 (5GHz):
#   RT-AX86U + RP-BE58 BSSIDs zatiaľ nezistené

# AP fallback — keď sa Pico nedokáže pripojiť na WiFi
AP_SSID = "PicoEnvStation"
AP_PASSWORD = "pico1234"
AP_IP = "192.168.4.1"

# Hardware piny
DHT_PIN = 16
DHT_MODEL = 11   # 11 alebo 22
BUTTON_PIN = 15

# Sieť
SERVER_PORT = 80
WIFI_RECONNECT_INTERVAL = 30  # sekundy medzi pokusmi o znovupripojenie po výpadku Wi-Fi

# Meranie senzora
# True  = meranie len na požiadanie (pri každom API volaní)
# False = intervalové meranie na pozadí
SENSOR_ON_DEMAND = True
SENSOR_INTERVAL = 2  # sekundy medzi meraniami (len ak SENSOR_ON_DEMAND = False)

# Debug režim — senzor ani tlačidlo sa neinicializujú, API vracia falošné hodnoty
DEBUG = False
DEBUG_TEMPERATURE = 25
DEBUG_HUMIDITY = 60
