import asyncio
import mss
import numpy as np
from bleak import BleakClient

ADDR = "5B:04:AA:71:16:C2"
WRITE_UUID = "0000ffe1-0000-1000-8000-00805F9B34FB"

EDGE_PX = 60


def sample_edges(img):
    h, w, _ = img.shape
    e = min(EDGE_PX, h // 4, w // 4)

    top = img[:e, :, :3].reshape(-1, 3)
    bottom = img[h - e:, :, :3].reshape(-1, 3)
    left = img[:, :e, :3].reshape(-1, 3)
    right = img[:, w - e:, :3].reshape(-1, 3)

    pixels = np.concatenate([top, bottom, left, right], axis=0)
    avg = pixels.mean(axis=0)

    b, g, r = avg.astype(int)
    return r, g, b


async def ambilight():
    print(f"Connecting to {ADDR}...")

    async with BleakClient(ADDR) as client:

        if not client.is_connected:
            print("Failed to connect.")
            return

        print("Connected!")

        await client.write_gatt_char(
            WRITE_UUID,
            bytearray([0xA0, 0x62, 0x01, 0x01]),
            response=True,
        )

        with mss.MSS() as sct:

            print("\nAvailable monitors:")

            # Skip monitor 0 because it represents the virtual desktop
            for i in range(1, len(sct.monitors)):
                m = sct.monitors[i]
                print(
                    f"{i}: {m['width']}x{m['height']} "
                    f"at ({m['left']}, {m['top']})"
                )

            while True:
                try:
                    monitor_num = int(input("\nSelect monitor number: "))

                    if 1 <= monitor_num < len(sct.monitors):
                        break

                    print("Invalid monitor number.")

                except ValueError:
                    print("Enter a valid number.")

            monitor = sct.monitors[monitor_num]

            print(f"\nUsing monitor {monitor_num}")
            print("Press Ctrl+C to stop.\n")

            while True:
                img = np.array(sct.grab(monitor))

                r, g, b = sample_edges(img)

                cmd = bytearray([
                    0xA0,
                    0x69,
                    0x04,
                    r,
                    g,
                    b,
                    255
                ])

                await client.write_gatt_char(
                    WRITE_UUID,
                    cmd,
                    response=False,
                )

                await asyncio.sleep(0.15)


async def main():
    try:
        await ambilight()
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())