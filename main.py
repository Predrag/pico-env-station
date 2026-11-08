from machine import Pin
import asyncio
import time
import config
from wifi_manager import WifiManager
from sensors import DHTSensor
import server
import dns_server
import network

led = Pin("LED", Pin.OUT)
button = Pin(config.BUTTON_PIN, Pin.IN, Pin.PULL_UP)
sensor = DHTSensor(pin=config.DHT_PIN, model=config.DHT_MODEL)

_current_mode = 'sta'  # 'sta' alebo 'ap'

def blink(count=1, on_s=0.2, off_s=0.2):
    for _ in range(count):
        led.on()
        time.sleep(on_s)
        led.off()
        time.sleep(off_s)

async def meranie():
    time.sleep(2)  # DHT11 potrebuje čas po zapnutí
    while True:
        try:
            sensor.measure()
            server.update_sensor_data(sensor.temperature, sensor.humidity)
            print(f"Teplota: {sensor.temperature} °C  Vlhkosť: {sensor.humidity} %")
        except OSError as e:
            print(f"Chyba čítania senzora: {e}")
        await asyncio.sleep(2)

async def button_handler(wifi):
    global _current_mode
    while True:
        if button.value() == 0:  # stlačené (PULL_UP = active LOW)
            if _current_mode == 'sta':
                wifi.stop_sta()
                ip = wifi.start_ap()
                _current_mode = 'ap'
                blink(3)
                print(f"[btn] Prepnuté na AP — pripoj sa na '{config.AP_SSID}', http://{ip}")
            else:
                wifi.stop_ap()
                if wifi.connect():
                    _current_mode = 'sta'
                    blink(2)
                    print(f"[btn] Prepnuté na WiFi: {wifi.ip()}")
                else:
                    wifi.start_ap()
                    blink(5)
                    print("[btn] WiFi nedostupné, zostávam v AP")
            await asyncio.sleep(0.5)  # debounce
        await asyncio.sleep(0.05)  # polling 20x za sekundu

async def main():
    global _current_mode
    blink(1)  # štart
    wifi = WifiManager(ssid=config.SSID, password=config.PASSWORD)
    print("Pripájam sa na Wi-Fi...")
    if wifi.connect():
        _current_mode = 'sta'
        blink(2)  # pripojené na Wi-Fi
        print(f"Pripojené! IP adresa: {wifi.ip()}")
        print(f"hostname: {network.WLAN(network.STA_IF).config('hostname')}")
    else:
        print("Wi-Fi zlyhalo, spúšťam AP režim...")
        ip = wifi.start_ap()
        _current_mode = 'ap'
        blink(3)  # AP režim aktívny
        print(f"AP aktívny — pripoj sa na '{config.AP_SSID}', otvor http://{ip}")

    await asyncio.gather(
        meranie(),
        server.run(config.SERVER_PORT),
        dns_server.run(config.AP_IP),
        button_handler(wifi)
    )

asyncio.run(main())
