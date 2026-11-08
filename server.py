import asyncio
import json
import gc

_temperature = None
_humidity = None

def update_sensor_data(temp, hum):
    global _temperature, _humidity
    _temperature = temp
    _humidity = hum

_STYLE = """
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: sans-serif; background: #1a1a2e; color: #eee; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; gap: 0; }}
    h1 {{ color: #e94560; margin-bottom: 2rem; font-size: 2rem; }}
    .cards {{ display: flex; gap: 1.5rem; flex-wrap: wrap; justify-content: center; }}
    .card {{ background: #16213e; border-radius: 16px; padding: 2rem 2.5rem; text-align: center; min-width: 160px; }}
    .value {{ font-size: 3.5rem; font-weight: bold; color: #e94560; }}
    .label {{ font-size: 0.9rem; color: #888; margin-top: 0.5rem; text-transform: uppercase; letter-spacing: 1px; }}
    .bar-wrap {{ background: #16213e; border-radius: 16px; padding: 1.5rem 2rem; width: 100%; max-width: 440px; margin-top: 1.5rem; }}
    .bar-label {{ display: flex; justify-content: space-between; margin-bottom: 0.75rem; font-size: 0.9rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }}
    .bar-track {{ background: #0f3460; border-radius: 8px; height: 20px; overflow: hidden; }}
    .bar-fill {{ background: #e94560; height: 100%; border-radius: 8px; width: {used_pct}%; }}
    .footer {{ margin-top: 2rem; color: #444; font-size: 0.8rem; }}
    a {{ color: #e94560; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
"""

_HTML = """<!DOCTYPE html>
<html lang="sk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Pico Teplomer</title>
    <style>{style}</style>
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
    <div class="footer"><a href="/memory">Pamäť RAM</a></div>
</body>
</html>"""

_HTML_MEMORY = """<!DOCTYPE html>
<html lang="sk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Pico — Pamäť RAM</title>
    <style>{style}</style>
</head>
<body>
    <h1>Pamäť RAM</h1>
    <div class="cards">
        <div class="card">
            <div class="value">{used_kb}</div>
            <div class="label">Použitá (KB)</div>
        </div>
        <div class="card">
            <div class="value">{free_kb}</div>
            <div class="label">Voľná (KB)</div>
        </div>
        <div class="card">
            <div class="value">{total_kb}</div>
            <div class="label">Celkom (KB)</div>
        </div>
    </div>
    <div class="bar-wrap">
        <div class="bar-label">
            <span>Využitie</span>
            <span>{used_pct}&nbsp;%</span>
        </div>
        <div class="bar-track">
            <div class="bar-fill"></div>
        </div>
    </div>
    <div class="footer"><a href="/">← Teplomer</a></div>
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

        elif path == '/api/memory':
            gc.collect()
            free = gc.mem_free()
            used = gc.mem_alloc()
            total = free + used
            body = json.dumps({
                "free_b": free,
                "used_b": used,
                "total_b": total,
                "used_pct": round(used / total * 100, 1) if total > 0 else 0.0
            })
            header = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
            writer.write((header + body).encode())

        elif path == '/memory':
            gc.collect()
            free = gc.mem_free()
            used = gc.mem_alloc()
            total = free + used
            used_pct = round(used / total * 100, 1) if total > 0 else 0.0
            style = _STYLE.format(used_pct=used_pct)
            body = _HTML_MEMORY.format(
                style=style,
                free_kb=round(free / 1024, 1),
                used_kb=round(used / 1024, 1),
                total_kb=round(total / 1024, 1),
                used_pct=used_pct
            )
            header = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
            writer.write((header + body).encode())

        elif path == '/':
            temp = _temperature if _temperature is not None else "--"
            hum = _humidity if _humidity is not None else "--"
            style = _STYLE.format(used_pct=0)
            body = _HTML.format(style=style, temp=temp, hum=hum)
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

async def run(port=80):
    server = await asyncio.start_server(_handle, '0.0.0.0', port)
    print("Server beží na porte 80")
    await server.wait_closed()
