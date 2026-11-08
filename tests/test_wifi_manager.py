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


def _make_manager_with_ap(ap_ip="192.168.4.1"):
    sta_mock = MagicMock()
    sta_mock.isconnected.return_value = True
    ap_mock = MagicMock()
    ap_mock.ifconfig.return_value = (ap_ip, "255.255.255.0", ap_ip, "0.0.0.0")
    sys.modules["network"].AP_IF = 1
    sys.modules["network"].STA_IF = 0
    sys.modules["network"].WLAN.side_effect = [sta_mock, ap_mock]
    return WifiManager(ssid="test", password="pass"), ap_mock


def test_start_ap_vrati_ip_adresu():
    manager, _ = _make_manager_with_ap(ap_ip="192.168.4.1")
    ip = manager.start_ap()
    assert ip == "192.168.4.1"


def test_start_ap_aktivuje_ap_interface():
    manager, ap_mock = _make_manager_with_ap()
    manager.start_ap()
    ap_mock.active.assert_called_with(True)


def test_start_ap_pouzije_zadany_ssid():
    manager, ap_mock = _make_manager_with_ap()
    manager.start_ap(ssid="MojPico", password="tajneheslo")
    ap_mock.config.assert_called_with(ssid="MojPico", password="tajneheslo")


def test_start_ap_ma_vychodzi_ssid():
    manager, ap_mock = _make_manager_with_ap()
    manager.start_ap()
    ap_mock.config.assert_called_with(ssid="PicoEnvStation", password="pico1234")


def test_stop_ap_deaktivuje_ap_interface():
    sta_mock = MagicMock()
    ap_mock = MagicMock()
    sys.modules["network"].AP_IF = 1
    sys.modules["network"].STA_IF = 0
    sys.modules["network"].WLAN.side_effect = [sta_mock, ap_mock]
    manager = WifiManager(ssid="test", password="pass")
    manager.stop_ap()
    ap_mock.active.assert_called_with(False)


def test_stop_sta_deaktivuje_sta_interface():
    sta_mock = MagicMock()
    sys.modules["network"].WLAN.side_effect = None  # reset po predchádzajúcom teste
    sys.modules["network"].WLAN.return_value = sta_mock
    sys.modules["network"].STA_IF = 0
    manager = WifiManager(ssid="test", password="pass")
    manager.stop_sta()
    sta_mock.active.assert_called_with(False)
