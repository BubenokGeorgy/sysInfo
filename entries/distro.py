import platform
from subprocess import check_output
from typing import Optional

from distributions import Distributions
from entry import Entry


class Distro(Entry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        distro_name = Distributions.get_distro_name()

        self.value = {"name": distro_name, "arch": platform.machine()}

    def output(self, output) -> None:
        output.append(
            self.name,
            f"{{}} {self.value['arch']}".format(
                self.value["name"] or self._default_strings.get("not_detected")
            ),
        )
