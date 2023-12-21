import os

from entry import Entry
from processes import Processes

DE_DICT = {
    "cinnamon": "Cinnamon",
    "dde-dock": "Deepin",
    "fur-box-session": "Fur Box",
    "gnome-session": "GNOME",
    "gnome-shell": "GNOME",
    "ksmserver": "KDE",
    "lxqt-session": "LXQt",
    "lxsession": "LXDE",
    "mate-session": "MATE",
    "xfce4-session": "Xfce",
}


class DesktopEnvironment(Entry):

    _PRETTY_NAME = "Desktop Environment"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        processes = Processes().list
        for de_id, de_name in DE_DICT.items():
            if de_id in processes:
                self.value = de_name
                break
        else:
            self.value = os.getenv("XDG_CURRENT_DESKTOP")
