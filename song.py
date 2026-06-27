import asyncio
import threading
import time
import numpy as np
import soundcard as sc
from bleak import BleakClient

ADDR = "58:01:EA:A7:17:2D"
WRITE_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

current_level = {"value": 0}
running = {"flag": True}


def audio_worker():
    """Runs in its own thread, never touches asyncio/BLE."""
    speaker = sc.default_speaker()
    mic = sc.get_microphone(speaker.name, include_loopback=True)
    with mic.recorder(samplerate=44100, blocksize=1024) as rec:
        while running["flag"]:
            data = rec.record(numframes=1024)
            volume = np.abs(data).mean()
            level = min(255, int(volume * 2000))  # tune multiplier to taste
            current_level["value"] = level


async def ble_worker():
    async with BleakClient(ADDR) as client:
        await client.write_gatt_char(WRITE_UUID, bytearray([0xA0, 0x62, 0x01, 0x01]), True)
        print("Connected. Reacting to audio... Ctrl+C to stop.")
        try:
            while True:
                level = current_level["value"]
                cmd = bytearray([0xA0, 0x69, 0x04, 255, 0, 0, level])
                await client.write_gatt_char(WRITE_UUID, cmd, False)
                await asyncio.sleep(0.08)
        except asyncio.CancelledError:
            pass


def main():
    t = threading.Thread(target=audio_worker, daemon=True)
    t.start()
    try:
        asyncio.run(ble_worker())
    except KeyboardInterrupt:
        pass
    finally:
        running["flag"] = False


if __name__ == "__main__":
    main()