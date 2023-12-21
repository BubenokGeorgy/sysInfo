import platform
from typing import Optional

from entry import Entry


class Hostname(Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = self._read_etc_hostname()
        if not self.value:
            self.value = platform.node()

    @staticmethod
    def _read_etc_hostname() -> Optional[str]:
        try:
            with open("/etc/hostname", encoding="UTF-8") as f_hostname:
                return f_hostname.read().rstrip()
        except FileNotFoundError:
            return None
