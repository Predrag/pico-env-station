from machine import Pin
import asyncio
import time
import config
from wifi_manager import WifiManager
from sensors import DHTSensor
import server
import network

led = Pin("LED", Pin.OUT)
sensor = DHTSensor(pin=16, model=11)

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

async def main():
    blink(1)  # štart
    wifi = WifiManager(ssid=config.SSID, password=config.PASSWORD)
    print("Pripájam sa na Wi-Fi...")
    if not wifi.connect():
        print("Chyba: Wi-Fi sa nepodarilo pripojiť.")
        return
    blink(2)  # pripojené na Wi-Fi
    print(f"Pripojené! IP adresa: {wifi.ip()}")
    print(f"hostname: {network.WLAN(network.STA_IF).config('hostname')}")

    await asyncio.gather(
        meranie(),
        server.run()
    )

asyncio.run(main())
