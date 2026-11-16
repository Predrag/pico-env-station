import sys
import asyncio
from unittest.mock import MagicMock, patch
import pytest

# socket nie je v conftest — dns_server.py ho vyžaduje pri importe
sys.modules['socket'] = MagicMock()

# Zabrání spusteniu asyncio.run(main()) pri importe main.py
with patch('asyncio.run'):
    import main as main_module


@pytest.fixture(autouse=True)
def reset_mode():
    main_module._current_mode = 'sta'
    yield
    main_module._current_mode = 'sta'


def _jednorazovy_sleep(first_raises=False):
    """
    first_raises=True: prvé volanie vyhodí CancelledError (preskočí telo slučky)
    first_raises=False: prvé volanie prebehne, druhé vyhodí CancelledError (jedna iterácia)
    """
    volania = 0

    async def sleep(s):
        nonlocal volania
        volania += 1
        if first_raises or volania >= 2:
            raise asyncio.CancelledError()

    return sleep


async def test_watchdog_nevola_connect_ak_je_spojeny():
    wifi = MagicMock()
    wifi.wlan.isconnected.return_value = True
    with patch('main.asyncio.sleep', new=_jednorazovy_sleep()):
        with pytest.raises(asyncio.CancelledError):
            await main_module.wifi_watchdog(wifi)
    wifi.connect.assert_not_called()


async def test_watchdog_nevola_connect_v_ap_rezime():
    wifi = MagicMock()
    wifi.wlan.isconnected.return_value = False
    main_module._current_mode = 'ap'
    with patch('main.asyncio.sleep', new=_jednorazovy_sleep()):
        with pytest.raises(asyncio.CancelledError):
            await main_module.wifi_watchdog(wifi)
    wifi.connect.assert_not_called()


async def test_watchdog_reconnect_ak_spojenie_vypadlo():
    wifi = MagicMock()
    wifi.wlan.isconnected.return_value = False
    wifi.connect.return_value = True
    wifi.ip.return_value = "192.168.1.50"
    with patch('main.asyncio.sleep', new=_jednorazovy_sleep()):
        with patch('main.blink'):
            with pytest.raises(asyncio.CancelledError):
                await main_module.wifi_watchdog(wifi)
    wifi.connect.assert_called_once()


async def test_watchdog_ohlasi_zlyhanie_reconnectu():
    wifi = MagicMock()
    wifi.wlan.isconnected.return_value = False
    wifi.connect.return_value = False
    with patch('main.asyncio.sleep', new=_jednorazovy_sleep()):
        with patch('main.blink'):
            with pytest.raises(asyncio.CancelledError):
                await main_module.wifi_watchdog(wifi)
    wifi.connect.assert_called_once()


async def test_watchdog_pouziva_interval_z_configu(monkeypatch):
    wifi = MagicMock()
    wifi.wlan.isconnected.return_value = True
    monkeypatch.setattr(main_module.config, 'WIFI_RECONNECT_INTERVAL', 60)
    zachyteny_interval = []

    async def fake_sleep(s):
        zachyteny_interval.append(s)
        raise asyncio.CancelledError()

    with patch('main.asyncio.sleep', new=fake_sleep):
        with pytest.raises(asyncio.CancelledError):
            await main_module.wifi_watchdog(wifi)
    assert zachyteny_interval[0] == 60
