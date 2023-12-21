import os
import typing
from subprocess import DEVNULL, CalledProcessError, check_output

from entry import Entry

PACKAGES_TOOLS = (
    {"cmd": ("apk", "list", "--installed")},  # Alpine Linux
    {"cmd": ("dpkg", "--get-selections")},  # Debian/Ubuntu Linux
    {"cmd": ("pacman", "-Q")},  # Arch Linux
    {"cmd": ("yum", "list", "installed"), "skew": 2},  # CentOS
)


class Packages(Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for packages_tool in PACKAGES_TOOLS:
            packages_tool = typing.cast(dict, packages_tool)

            try:
                results = check_output(
                    packages_tool["cmd"],
                    stderr=DEVNULL,
                    env={
                        **os.environ,
                        "LANG": "C",
                    },
                    universal_newlines=True,
                )
            except (OSError, CalledProcessError):
                continue

            if self.value:
                self.value += results.count("\n")
            else:
                self.value = results.count("\n")

            if "skew" in packages_tool:
                self.value -= packages_tool["skew"]

            if packages_tool["cmd"][0] == "dpkg":
                self.value -= results.count("deinstall")

