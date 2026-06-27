import asyncio
import mss
import numpy as np
from bleak import BleakClient

ADDR = "58:01:EA:A7:17:2D"
WRITE_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

EDGE_PX = 60

def sample_edges(img):
    h, w, _ = img.shape
    e = min(EDGE_PX, h // 4, w // 4)
    top = img[0:e, :, :3].reshape(-1, 3)
    bottom = img[h - e:h, :, :3].reshape(-1, 3)
    left = img[:, 0:e, :3].reshape(-1, 3)
    right = img[:, w - e:w, :3].reshape(-1, 3)
    all_edge_pixels = np.concatenate([top, bottom, left, right], axis=0)
    avg = all_edge_pixels.mean(axis=0)
    b, g, r = avg.astype(int)
    return r, g, b

async def ambilight():
    async with BleakClient(ADDR) as client:
        await client.write_gatt_char(WRITE_UUID, bytearray([0xA0, 0x62, 0x01, 0x01]), True)
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            while True:
                img = np.array(sct.grab(monitor))
                r, g, b = sample_edges(img)
                cmd = bytearray([0xA0, 0x69, 0x04, r, g, b, 255])
                await client.write_gatt_char(WRITE_UUID, cmd, False)
                await asyncio.sleep(0.15)

asyncio.run(ambilight())