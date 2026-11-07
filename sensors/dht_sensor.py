import dht
from machine import Pin


class DHTSensor:
    def __init__(self, pin, model=11):
        if model == 22:
            self._sensor = dht.DHT22(Pin(pin))
        else:
            self._sensor = dht.DHT11(Pin(pin))
        self._temperature = None
        self._humidity = None

    def measure(self):
        self._sensor.measure()
        self._temperature = self._sensor.temperature()
        self._humidity = self._sensor.humidity()

    @property
    def temperature(self):
        return self._temperature

    @property
    def humidity(self):
        return self._humidity
