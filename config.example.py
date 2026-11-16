SSID = "your_wifi_ssid"
PASSWORD = "your_wifi_password"

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
