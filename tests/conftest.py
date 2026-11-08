import sys
import gc
from unittest.mock import MagicMock

# MicroPython moduly neexistujú na PC — nahradíme ich mock-mi pred akýmkoľvek importom
sys.modules['machine'] = MagicMock()
sys.modules['dht'] = MagicMock()
sys.modules['network'] = MagicMock()

# gc.mem_free / gc.mem_alloc existujú len v MicroPythone
if not hasattr(gc, 'mem_free'):
    gc.mem_free = lambda: 0
if not hasattr(gc, 'mem_alloc'):
    gc.mem_alloc = lambda: 0
