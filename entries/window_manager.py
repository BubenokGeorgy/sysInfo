import re
from subprocess import DEVNULL, CalledProcessError, check_output

from entry import Entry
from processes import Processes

WM_DICT = {
    "awesome": "Awesome",
    "bspwm": "bspwm",
    "cinnamon": "Cinnamon",
    "dwm": "DWM",
    "i3": "i3",
    "openbox": "Openbox",
    "qtile": "QTile",
    "spectrwm": "SpectrWM",
    "xfwm4": "Xfwm",
    "xmonad": "Xmonad",
}


class WindowManager(Entry):

    _PRETTY_NAME = "Window Manager"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.value = re.search(
                r"(?<=Name: ).*",
                check_output(["wmctrl", "-m"], stderr=DEVNULL, universal_newlines=True),
            ).group(0)
        except (FileNotFoundError, CalledProcessError):
            processes = Processes().list
            for wm_id, wm_name in WM_DICT.items():
                if wm_id in processes:
                    self.value = wm_name
                    break
