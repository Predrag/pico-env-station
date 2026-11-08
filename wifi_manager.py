import config
import network
import time

class WifiManager:
    def __init__(self, ssid, password, hostname="pico"):
        self.ssid = ssid
        self.password = password
        self.hostname = hostname
        self.wlan = network.WLAN(network.STA_IF)

    def connect(self, timeout=15):
        self.wlan.active(False)
        network.hostname(self.hostname)
        self.wlan.active(True)
        if not self.wlan.isconnected():
            self.wlan.connect(self.ssid, self.password)
            for _ in range(timeout):
                if self.wlan.isconnected():
                    break
                time.sleep(1)
        return self.wlan.isconnected()

    def ip(self):
        return self.wlan.ifconfig()[0]

    def start_ap(self, ssid=config.AP_SSID, password=config.AP_PASSWORD):
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        network.hostname(self.hostname)
        ap.config(ssid=ssid, password=password)
        ap.active(True)
        return ap.ifconfig()[0]

    def stop_ap(self):
        ap = network.WLAN(network.AP_IF)
        ap.active(False)

    def stop_sta(self):
        self.wlan.active(False)
