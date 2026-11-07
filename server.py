import asyncio
import json

_temperature = None
_humidity = None

def update_sensor_data(temp, hum):
    global _temperature, _humidity
    _temperature = temp
    _humidity = hum

_HTML = """<!DOCTYPE html>
<html lang="sk">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Pico Teplomer</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: sans-serif; background: #1a1a2e; color: #eee; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }}
        h1 {{ color: #e94560; margin-bottom: 2rem; font-size: 2rem; }}
        .cards {{ display: flex; gap: 1.5rem; flex-wrap: wrap; justify-content: center; }}
        .card {{ background: #16213e; border-radius: 16px; padding: 2rem 2.5rem; text-align: center; min-width: 160px; }}
        .value {{ font-size: 3.5rem; font-weight: bold; color: #e94560; }}
        .label {{ font-size: 0.9rem; color: #888; margin-top: 0.5rem; text-transform: uppercase; letter-spacing: 1px; }}
        .footer {{ margin-top: 2rem; color: #444; font-size: 0.8rem; }}
    </style>
</head>
<body>
    <h1>Pico Teplomer</h1>
    <div class="cards">
        <div class="card">
            <div class="value">{temp}&nbsp;°C</div>
            <div class="label">Teplota</div>
        </div>
        <div class="card">
            <div class="value">{hum}&nbsp;%</div>
            <div class="label">Vlhkosť</div>
        </div>
    </div>
    <div class="footer">Obnoví sa automaticky každých 5 sekúnd</div>
</body>
</html>"""

async def _handle(reader, writer):
    try:
        request = await reader.read(512)
        path = request.decode().split(' ')[1] if b' ' in request else '/'


        if path == '/api/temperature':
            body = json.dumps({
                "temperature": _temperature,
                "humidity": _humidity,
                "unit": "celsius"
            })
            header = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
            writer.write((header + body).encode())

        elif path == '/':
            temp = _temperature if _temperature is not None else "--"
            hum = _humidity if _humidity is not None else "--"
            body = _HTML.format(temp=temp, hum=hum)
            header = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
            writer.write((header + body).encode())

        else:
            writer.write(b"HTTP/1.1 404 Not Found\r\n\r\nNot Found")

        await writer.drain()
    except OSError:
        pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except OSError:
            pass

async def run():
    server = await asyncio.start_server(_handle, '0.0.0.0', 80)
    print("Server beží na porte 80")
    await server.wait_closed()
