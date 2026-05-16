from buttplug import ButtplugClient
from device import Device

class Client:
    def __init__(self):
        self.devices = dict()
        self.bp = ButtplugClient("My App")
        
    
    def __on_device_added(self, dv):
        device = Device(dv)
        self.devices[device.name] = device
        
    async def Connect(self):
        self.bp.on_device_added = self.__on_device_added
        await self.bp.connect("ws://127.0.0.1:12345")

        # Scan for devices
        while not (self.devices or None):
            await self.bp.disconnect()
            await self.bp.connect("ws://127.0.0.1:12345")
            await self.bp.start_scanning()
        await self.bp.stop_scanning()

    