import asyncio, time
from threading import Thread, Event
from client import Client
from input.listener import KeyListener
from typing import Optional
from device import Device

class _G:
    # global namespace
    loop        = None
    stop_event  = Event()
    
class DevCtl:
    device: Optional[Device]    = None
    pause                       = False
    
    class Osc:
        lo  = 0
        hi  = 99
        spd = 1000
            
        class Rand:
            # randomness for position and duration
            pos_state   = False
            pos_val     = 0.25
            dur_state   = False
            dur_val     = 0.15

def input_listener():
    global key
    listener = KeyListener()
    last_key = None
    def set_once(key,obj,var,val):
        nonlocal last_key
        if not last_key == key:
            setattr(obj,var,val)
            last_key = key
                   
    while True:
        hk=listener.key()
        match hk:
            case "pause":
                set_once(hk,DevCtl,"pause", not DevCtl.pause)
            case "num_add":
                set_once(hk,DevCtl.Osc,"spd",DevCtl.Osc.spd-100)
            case "num_subtract":
                set_once(hk,DevCtl.Osc,"spd",DevCtl.Osc.spd+100)
            case "num_divide":
                set_once(hk,DevCtl.Osc.Rand,"dur_state",not DevCtl.Osc.Rand.dur_state)
            case "num_multiply":
                set_once(hk,DevCtl.Osc.Rand,"pos_state",not DevCtl.Osc.Rand.pos_state)
            case "num_1":
                DevCtl.Osc.lo = 70
                DevCtl.Osc.hi = 99
            case "num_2":
                DevCtl.Osc.lo = 40
                DevCtl.Osc.hi = 70
            case "num_3":
                DevCtl.Osc.lo = 0
                DevCtl.Osc.hi = 40
            case _:
                DevCtl.Osc.lo = 0
                DevCtl.Osc.hi = 99
                last_key = None
                
        print(
            f"""
            Pause:          {DevCtl.pause}\n
            Osc.lo:         {DevCtl.Osc.lo}\n
            Osc.hi:         {DevCtl.Osc.hi}\n
            Osc.spd:        {DevCtl.Osc.spd}\n
            Osc.Rand.pos:   {DevCtl.Osc.Rand.pos_state}\n
            Osc.Rand.dur:   {DevCtl.Osc.Rand.dur_state}\n
            """
        )
        time.sleep(0.1)
            
            
async def start_client():
    c=Client()
    await c.Connect()
    DevCtl.device = list(c.devices.values())[0]
    
async def device_loop():
    await start_client()
    while True:
        if DevCtl.device is None:
            raise RuntimeError("Device is not connected yet")
        await DevCtl.device.lwt.oscillate(
            [
                DevCtl.Osc.lo,
                DevCtl.Osc.hi
            ],
            DevCtl.Osc.spd,
            DevCtl.Osc.Rand.pos_state,
            DevCtl.Osc.Rand.dur_state
        )

input_thread = Thread(target=input_listener)
input_thread.start()

try:
    asyncio.run(device_loop())
except BaseException:
    _G.stop_event.set()
    #device_thread.join()
    raise