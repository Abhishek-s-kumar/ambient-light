import asyncio
import sys
from bleak import BleakClient

ADDR = "58:01:EA:A7:17:2D"
WRITE_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"


async def send(client, data: bytearray):
    print("Sending:", data.hex())
    await client.write_gatt_char(WRITE_UUID, data, response=True)
    await asyncio.sleep(0.3)


async def power(client, on: bool):
    await send(client, bytearray([0xA0, 0x62, 0x01, 0x01 if on else 0x00]))


async def set_color(client, r: int, g: int, b: int, level: int = 255):
    await power(client, True)
    await send(client, bytearray([0xA0, 0x69, 0x04, r, g, b, level]))


async def main():
    async with BleakClient(ADDR) as client:
        print("Connected:", client.is_connected)

        if len(sys.argv) == 2 and sys.argv[1] == "off":
            await power(client, False)
            return

        if len(sys.argv) == 4:
            r, g, b = (int(x) for x in sys.argv[1:4])
        else:
            r, g, b = 255, 0, 0  # default red

        await set_color(client, r, g, b)
        print(f"Set color to ({r},{g},{b})")


asyncio.run(main())