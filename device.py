import random, asyncio
from BP import OutputType, DeviceOutputCommand

class Device:
    def __init__(self, device):
        self.__device   = device
        self.name       = device.name
        self.index      = device.index
        match list(device.features[0].outputs.keys())[0]:
            case "HwPositionWithDuration":
                self.type  = "LinearWithTime"
                self.ctl   = LinearWithTime(device)
            case None:
                self.type = None
    
class LinearWithTime(Device):
    def __init__(self, device):
        self.__device           = device
        self._min_delay         = device.message_timing_gap
        self._min_pos           = device.features[0].step_range(OutputType.POSITION_WITH_DURATION)[0]
        self._max_pos           = device.features[0].step_range(OutputType.POSITION_WITH_DURATION)[1]
        self._min_duration      = device.features[0].duration_range(OutputType.POSITION_WITH_DURATION)[0]
        self._max_duration      = device.features[0].duration_range(OutputType.POSITION_WITH_DURATION)[1]
        self.name               = device.name
        self.oscillate          = self.Oscillate(self)
        
    async def set_pos(self, position, speed):
        if self.__device:
            await self.__device.run_output(DeviceOutputCommand(OutputType.POSITION_WITH_DURATION, position, speed))
            await asyncio.sleep(speed/1000 + self._min_delay/1000)
        
    class Oscillate:
        def __init__(self, device) -> None:
            self.device = device
            self.pause  = True
            self.halt   = False
            self.lower  = 0
            self.upper  = 99
            self.speed  = 1000
            # randomness for position and duration
            self.rand_pos_state   = False
            self.rand_pos_val     = 0.25
            self.rand_dur_state   = False
            self.rand_dur_val     = 0.15
            
        async def __call__(self):
            self.halt   = False
            while True:
                if self.halt:
                    return
                
                if self.pause:
                    await asyncio.sleep(0.1)
                    continue
                
                high    = self._randomize(self.lower, self.rand_pos_val, self.device._min_pos, self.device._max_pos)
                low     = self._randomize(self.upper, self.rand_pos_val, self.device._min_pos, self.device._max_pos)

                # Preserve interval rule: first value should stay higher.
                if low > high:
                    high, low = low, high

                speed_1 = self._randomize(self.speed, self.rand_dur_val, self.device._min_duration, self.device._max_duration)
                speed_2 = self._randomize(self.speed, self.rand_dur_val, self.device._min_duration, self.device._max_duration)

                await self.device.set_pos(high, speed_1)
                await self.device.set_pos(low,  speed_2)
        
        def reset(self):
            self.lower  = 0
            self.upper  = 99
            self.speed  = 1000
            # randomness for position and duration
            self.rand_pos_state   = False
            self.rand_pos_val     = 0.25
            self.rand_dur_state   = False
            self.rand_dur_val     = 0.15
            
        def stop(self):
            self.halt   = True
            self.pause  = True
            self.reset()
            
        def _randomize(self, value, factor, min_value, max_value):
            def clamp(value, min_value, max_value):
                return max(min_value, min(value, max_value))

            delta = value * factor
            randomized = random.uniform(value - delta, value + delta)
            return clamp(round(randomized), min_value, max_value)