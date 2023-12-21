import json
import platform
from socket import timeout as SocketTimeoutError
from typing import Optional
from urllib.error import URLError
from urllib.request import urlopen

from entry import Entry
from environment import Environment
from utility import Utility


class Kernel(Entry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = {
            "name": platform.system(),
            "release": platform.release(),
            "latest": None,
            "is_outdated": None,
        }

        if (
            self.value["name"] != "Linux"
            or Environment.DO_NOT_TRACK
        ):
            return

        self.value["latest"] = self._fetch_latest_linux_release()
        if self.value["latest"]:
            self.value["is_outdated"] = Utility.version_to_semver_segments(
                self.value["release"]
            ) < Utility.version_to_semver_segments(self.value["latest"])

    @staticmethod
    def _fetch_latest_linux_release() -> Optional[str]:
        try:
            with urlopen("https://www.kernel.org/releases.json") as http_request:
                try:
                    kernel_releases = json.load(http_request)
                except json.JSONDecodeError:
                    return None
        except (URLError, SocketTimeoutError):
            return None

        return kernel_releases.get("latest_stable", {}).get("version")

    def output(self, output) -> None:
        text_output = " ".join((self.value["name"], self.value["release"]))

        if self.value["latest"]:
            if self.value["is_outdated"]:
                text_output += f" ({self.value['latest']} {self._default_strings.get('available')})"
            else:
                text_output += f" ({self._default_strings.get('latest')})"

        output.append(self.name, text_output)
