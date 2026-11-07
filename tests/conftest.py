import sys
from unittest.mock import MagicMock

# MicroPython moduly neexistujú na PC — nahradíme ich mock-mi pred akýmkoľvek importom
sys.modules['machine'] = MagicMock()
sys.modules['dht'] = MagicMock()
sys.modules['network'] = MagicMock()
