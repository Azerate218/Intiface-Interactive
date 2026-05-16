import random, time, asyncio
import threading
from buttplug import OutputType, DeviceOutputCommand

class Device:
    def __init__(self, device):
        self.__device   = device
        self.name       = device.name
        self.index      = device.index
        match list(device.features[0].outputs.keys())[0]:
            case "HwPositionWithDuration":
                self.type   = "LinearWithTime"
                self.lwt    = LinearWithTime(device)
            case None:
                self.type = None
            
    def _randomize(self, value, factor, min_value, max_value):
        def clamp(value, min_value, max_value):
            return max(min_value, min(value, max_value))

        delta = value * factor
        randomized = random.uniform(value - delta, value + delta)
        return clamp(round(randomized), min_value, max_value)
    
class LinearWithTime(Device):
    def __init__(self, device):
        self.__device           = device
        self.name               = device.name
        self.min_delay          = device.message_timing_gap
        self.min_pos            = device.features[0].step_range(OutputType.POSITION_WITH_DURATION)[0]
        self.max_pos            = device.features[0].step_range(OutputType.POSITION_WITH_DURATION)[1]
        self.min_duration       = device.features[0].duration_range(OutputType.POSITION_WITH_DURATION)[0]
        self.max_duration       = device.features[0].duration_range(OutputType.POSITION_WITH_DURATION)[1]
        self.output_end_time    = 0
        
    async def set_pos(self, position, speed):
        #print(f"set_pos():\npos: {position} speed: {speed}")
        #print(time.time() - self.output_end_time)
        if self.__device:
            await self.__device.run_output(DeviceOutputCommand(OutputType.POSITION_WITH_DURATION, position, speed))
            await asyncio.sleep(speed/1000 + self.min_delay/1000)
                

    async def oscillate(self, interval, speed, rand_interval=0, rand_speed=0):
        high     = super()._randomize(interval[0], rand_interval, self.min_pos, self.max_pos)
        low      = super()._randomize(interval[1], rand_interval, self.min_pos, self.max_pos)

        # Preserve interval rule: first value should stay higher.
        if low > high:
            high, low = low, high

        speed_1 = super()._randomize(speed, rand_speed, self.min_duration, self.max_duration)
        speed_2 = super()._randomize(speed, rand_speed, self.min_duration, self.max_duration)

        await self.set_pos(high, speed_1)
        await self.set_pos(low, speed_2)
        
        
