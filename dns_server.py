import socket
import asyncio


async def run(ip="192.168.4.1"):
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind(("0.0.0.0", 53))
    udp.setblocking(False)
    ip_bytes = bytes(int(x) for x in ip.split('.'))

    while True:
        try:
            data, addr = udp.recvfrom(512)
            response = bytearray(data[:2])      # transaction ID z dotazu
            response += b'\x81\x80'             # flags: response, no error
            response += data[4:6]               # počet otázok
            response += b'\x00\x01'             # počet odpovedí: 1
            response += b'\x00\x00\x00\x00'     # authority + additional: 0
            response += data[12:]               # sekcia otázky (zrkadlo)
            response += b'\xc0\x0c'             # pointer na meno v otázke
            response += b'\x00\x01'             # typ: A
            response += b'\x00\x01'             # trieda: IN
            response += b'\x00\x00\x00\x3c'     # TTL: 60 sekúnd
            response += b'\x00\x04'             # dĺžka dát: 4 bajty
            response += ip_bytes                # IP adresa Pica
            udp.sendto(bytes(response), addr)
        except OSError:
            pass
        await asyncio.sleep(0.1)
