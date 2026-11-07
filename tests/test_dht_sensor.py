import sys
from unittest.mock import MagicMock
from sensors.dht_sensor import DHTSensor


def _mock_hw(temp, humidity):
    hw = MagicMock()
    hw.temperature.return_value = temp
    hw.humidity.return_value = humidity
    return hw


def test_teplota_je_none_pred_meranim():
    sensor = DHTSensor(pin=16, model=11)
    assert sensor.temperature is None


def test_vlhkost_je_none_pred_meranim():
    sensor = DHTSensor(pin=16, model=11)
    assert sensor.humidity is None


def test_measure_ulozi_teplotu():
    hw = _mock_hw(temp=25, humidity=60)
    sys.modules["dht"].DHT11.return_value = hw
    sensor = DHTSensor(pin=16, model=11)
    sensor.measure()
    assert sensor.temperature == 25


def test_measure_ulozi_vlhkost():
    hw = _mock_hw(temp=25, humidity=60)
    sys.modules["dht"].DHT11.return_value = hw
    sensor = DHTSensor(pin=16, model=11)
    sensor.measure()
    assert sensor.humidity == 60


def test_pouzije_dht11_pre_model_11():
    sys.modules["dht"].DHT11.reset_mock()
    DHTSensor(pin=16, model=11)
    sys.modules["dht"].DHT11.assert_called_once()


def test_pouzije_dht22_pre_model_22():
    sys.modules["dht"].DHT22.reset_mock()
    DHTSensor(pin=16, model=22)
    sys.modules["dht"].DHT22.assert_called_once()


def test_pouzije_dht11_pre_neznamy_model():
    sys.modules["dht"].DHT11.reset_mock()
    DHTSensor(pin=16, model=99)
    sys.modules["dht"].DHT11.assert_called_once()
