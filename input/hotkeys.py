import json
from pathlib import Path

class Hotkeys:
    __SCRIPT_DIR = Path(__file__).resolve().parent
    hotkeys = json.loads((__SCRIPT_DIR / "hotkeys.json").read_text(encoding="utf-8"))
    last_key = None
    
    
    @classmethod
    def set_once(cls,key,obj,var,val):
        if not cls.last_key == key:
            setattr(obj,var,val)
            cls.last_key = key
            
        