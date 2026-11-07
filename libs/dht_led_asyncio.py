import dht
from machine import Pin
import asyncio

# GP16 = DHT11 DATA, GP15 = tlačidlo, GP14 = LED
sensor = dht.DHT11(Pin(16))
tlacidlo = Pin(15, Pin.IN, Pin.PULL_UP)
led = Pin(14, Pin.OUT)

async def meranie():
    await asyncio.sleep(2)  # štartovacia pauza, neblokuje
    while True:
        try:
            sensor.measure()
            print(f"Teplota: {sensor.temperature()} °C")
            print(f"Vlhkosť: {sensor.humidity()} %")
        except OSError as e:
            print(f"Chyba čítania: {e}")
        await asyncio.sleep(2)

async def ovladanie_led():
    while True:
        if tlacidlo.value() == 0:  # stlačené (PULL_UP = active LOW)
            led.toggle()
            await asyncio.sleep(0.3)  # debounce
        await asyncio.sleep(0.05)  # kontrola 20x za sekundu

async def main():
    await asyncio.gather(
        meranie(),
        ovladanie_led()
    )

asyncio.run(main())
