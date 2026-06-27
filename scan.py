import asyncio
from bleak import BleakScanner

async def main():
    print("Scanning 8 seconds...")
    devices = await BleakScanner.discover(timeout=8.0)
    for d in devices:
        print(d.address, "-", d.name)

asyncio.run(main())