import pytest
import json
from unittest.mock import patch
import server


class FakeReader:
    def __init__(self, path="/"):
        self._data = f"GET {path} HTTP/1.1\r\n".encode()

    async def read(self, n):
        return self._data


class FakeWriter:
    def __init__(self):
        self.data = b""

    def write(self, data):
        self.data += data

    async def drain(self):
        pass

    async def wait_closed(self):
        pass

    def close(self):
        pass


@pytest.fixture(autouse=True)
def reset_server_state():
    server._temperature = None
    server._humidity = None
    yield


def test_update_sensor_data_ulozi_hodnoty():
    server.update_sensor_data(25.5, 60)
    assert server._temperature == 25.5
    assert server._humidity == 60


def test_update_sensor_data_prepise_predchadzajuce_hodnoty():
    server.update_sensor_data(20, 50)
    server.update_sensor_data(30, 70)
    assert server._temperature == 30
    assert server._humidity == 70


@pytest.mark.asyncio
async def test_api_temperature_vrati_spravny_json():
    server.update_sensor_data(22, 55)
    writer = FakeWriter()
    await server._handle(FakeReader("/api/temperature"), writer)
    body = writer.data.split(b"\r\n\r\n", 1)[1]
    data = json.loads(body)
    assert data["temperature"] == 22
    assert data["humidity"] == 55
    assert data["unit"] == "celsius"


@pytest.mark.asyncio
async def test_api_temperature_content_type_je_json():
    server.update_sensor_data(22, 55)
    writer = FakeWriter()
    await server._handle(FakeReader("/api/temperature"), writer)
    assert b"application/json" in writer.data


@pytest.mark.asyncio
async def test_root_vrati_html_s_hodnotami():
    server.update_sensor_data(20, 50)
    writer = FakeWriter()
    await server._handle(FakeReader("/"), writer)
    assert b"20" in writer.data
    assert b"50" in writer.data
    assert b"text/html" in writer.data


@pytest.mark.asyncio
async def test_root_zobrazuje_placeholder_bez_dat():
    writer = FakeWriter()
    await server._handle(FakeReader("/"), writer)
    assert b"--" in writer.data


@pytest.mark.asyncio
async def test_api_memory_vrati_json_s_ram():
    with patch('gc.mem_free', return_value=100000), \
         patch('gc.mem_alloc', return_value=50000):
        writer = FakeWriter()
        await server._handle(FakeReader("/api/memory"), writer)
        body = writer.data.split(b"\r\n\r\n", 1)[1]
        data = json.loads(body)
        assert data["free_b"] == 100000
        assert data["used_b"] == 50000
        assert data["total_b"] == 150000
        assert data["used_pct"] == 33.3


@pytest.mark.asyncio
async def test_api_memory_content_type_je_json():
    with patch('gc.mem_free', return_value=80000), \
         patch('gc.mem_alloc', return_value=20000):
        writer = FakeWriter()
        await server._handle(FakeReader("/api/memory"), writer)
        assert b"application/json" in writer.data


@pytest.mark.asyncio
async def test_memory_stranka_obsahuje_kb_hodnoty():
    with patch('gc.mem_free', return_value=200*1024), \
         patch('gc.mem_alloc', return_value=50*1024):
        writer = FakeWriter()
        await server._handle(FakeReader("/memory"), writer)
        assert b"text/html" in writer.data
        assert b"200.0" in writer.data  # free_kb
        assert b"50.0" in writer.data   # used_kb


@pytest.mark.asyncio
async def test_memory_stranka_obsahuje_odkaz_na_hlavnu():
    with patch('gc.mem_free', return_value=100*1024), \
         patch('gc.mem_alloc', return_value=50*1024):
        writer = FakeWriter()
        await server._handle(FakeReader("/memory"), writer)
        assert b'href="/"' in writer.data


@pytest.mark.asyncio
async def test_root_obsahuje_odkaz_na_memory():
    writer = FakeWriter()
    await server._handle(FakeReader("/"), writer)
    assert b'href="/memory"' in writer.data


@pytest.mark.asyncio
async def test_neznama_cesta_vrati_404():
    writer = FakeWriter()
    await server._handle(FakeReader("/neexistuje"), writer)
    assert b"404" in writer.data
