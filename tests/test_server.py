import pytest
import json
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
async def test_neznama_cesta_vrati_404():
    writer = FakeWriter()
    await server._handle(FakeReader("/neexistuje"), writer)
    assert b"404" in writer.data
