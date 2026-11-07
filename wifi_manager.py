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
