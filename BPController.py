import asyncio, time
from threading import Thread, Event
from client import Client
from device import Device
from input.listener import KeyListener
from typing import Optional

class _G:
    # global namespace
    loop                        = None
    device: Optional[Device]    = None
    stop_event                  = Event()

def input_listener():
    listener = KeyListener()
    while _G.device is None:
        time.sleep(0.1)
        continue

async def start_client():
    c=Client()
    await c.Connect()
    _G.device = list(c.devices.values())[0]
    
async def device_loop():
    await start_client()
    if _G.device is None:
        raise RuntimeError("Device is not connected yet")
    await _G.device.ctl.oscillate()

input_thread = Thread(target=input_listener)
input_thread.start()

try:
    asyncio.run(device_loop())
except BaseException:
    _G.stop_event.set()
    #device_thread.join()
    raise