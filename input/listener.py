import json
import sys
from pathlib import Path
from pynput.keyboard import Listener


class KeyListener:
    VK_CapsLock    = 0x14
    VK_NumLock     = 0x90
    VK_ScrollLock  = 0x91
    __SCRIPT_DIR = Path(__file__).resolve().parent
    __hk_names = json.loads((__SCRIPT_DIR / "hk_names.json").read_text(encoding="utf-8"))

    def __init__(self):
        self.__pressed_keys = list()

        def key_name(key):
            vk = getattr(key, "vk", None) or getattr(getattr(key, "value", None), "vk", None)

            if vk is not None:
                name = self.__hk_names["VK_NAMES"].get(f"0x{vk:02X}")
                if name:
                    return name
            
            #fallbacks for uncommon setups and numlock 5:
            name = self.__hk_names["KEY_NAMES"].get(str(key))
            if name:
                return name

            if hasattr(key, "char") and key.char:
                return key.char.lower()

            return str(key).removeprefix("Key.")

        def __on_press(key):
            name = key_name(key)
            if name not in self.__pressed_keys:
                self.__pressed_keys.append(name)


        def __on_release(key):
            name = key_name(key)
            if name in self.__pressed_keys:
                self.__pressed_keys.remove(name)

        """     
        def on_press(key):
            async def handle_press(key):
                pressed_keys.append(key_name(key))
            asyncio.run_coroutine_threadsafe(handle_press(key), k_loop)

        def on_release(key):
            async def handle_release(key):
                pressed_keys.remove(key_name(key))
            asyncio.run_coroutine_threadsafe(handle_release(key), k_loop)
        """
        self.__listener = Listener(on_press=__on_press, on_release=__on_release)
        self.__listener.start()
    
    def key(self):
        if not self.__pressed_keys:
            return None
        return str(self.__pressed_keys[-1])
    
    def key_list(self):
        if not self.__pressed_keys:
            return None
        return list(self.__pressed_keys)
    
    def is_lock_on(self, vk:int) -> bool:
        if sys.platform != "win32":
            raise RuntimeError("Num Lock state detection requires Windows Python.")

        import ctypes

        return bool(ctypes.windll.user32.GetKeyState(vk) & 1)


    def set_lock(self, vk:int,state:bool) -> bool:

        if self.is_lock_on(vk) == state:
            return self.is_lock_on(vk)
    
        import ctypes

        KEYEVENTF_EXTENDEDKEY = 0x0001
        KEYEVENTF_KEYUP = 0x0002

        ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_EXTENDEDKEY, 0)
        ctypes.windll.user32.keybd_event(
            vk,
            0,
            KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP,
            0,
        )
        return self.is_lock_on(vk)

if __name__ == "__main__":
    listener = KeyListener()
    print(listener.set_lock(listener.VK_CapsLock,False))

    while True:
        print(listener.key_list())
