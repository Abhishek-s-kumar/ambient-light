import asyncio
import mss
import numpy as np
from bleak import BleakClient

ADDR = "58:01:EA:A7:17:2D"
WRITE_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

async def ambilight():
    async with BleakClient(ADDR) as client:
        await client.write_gatt_char(WRITE_UUID, bytearray([0xA0, 0x62, 0x01, 0x01]), True)
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            while True:
                img = np.array(sct.grab(monitor))
                avg = img[:, :, :3].mean(axis=(0, 1))  # BGRA -> avg B,G,R
                b, g, r = avg.astype(int)
                cmd = bytearray([0xA0, 0x69, 0x04, r, g, b, 255])
                await client.write_gatt_char(WRITE_UUID, cmd, False)
                await asyncio.sleep(0.15)  # ~6-7 updates/sec, don't flood BLE

asyncio.run(ambilight())