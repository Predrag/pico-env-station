import sys
from unittest.mock import MagicMock
from wifi_manager import WifiManager


def _make_manager(connected=True, ip="192.168.1.100"):
    wlan = MagicMock()
    wlan.isconnected.return_value = connected
    wlan.ifconfig.return_value = (ip, "255.255.255.0", "192.168.1.1", "8.8.8.8")
    sys.modules["network"].WLAN.return_value = wlan
    sys.modules["network"].STA_IF = 0
    return WifiManager(ssid="testnet", password="testpass")


def test_connect_vrati_true_ak_je_pripojeny():
    manager = _make_manager(connected=True)
    assert manager.connect() is True


def test_connect_vrati_false_po_timeout():
    manager = _make_manager(connected=False)
    assert manager.connect(timeout=1) is False


def test_ip_vrati_adresu():
    manager = _make_manager(ip="10.0.0.5")
    assert manager.ip() == "10.0.0.5"


def test_hostname_ma_default_hodnotu():
    manager = _make_manager()
    assert manager.hostname == "pico"


def test_hostname_sa_da_nastavit():
    sys.modules["network"].WLAN.return_value = MagicMock()
    manager = WifiManager(ssid="net", password="pass", hostname="moj-pico")
    assert manager.hostname == "moj-pico"
