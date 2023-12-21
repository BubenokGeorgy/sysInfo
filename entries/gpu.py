import platform
from subprocess import DEVNULL, CalledProcessError, check_output
from typing import List

from entry import Entry


class GPU(Entry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if platform.system() == "Linux":
            self.value = self._parse_lspci_output()

        max_count = self.options.get("max_count", 2)
        if max_count is not False:
            self.value = self.value[:max_count]

    @staticmethod
    def _parse_lspci_output() -> List[str]:
        try:
            lspci_output = check_output("lspci", universal_newlines=True).splitlines()
        except (FileNotFoundError, CalledProcessError):
            return []

        gpus_list = []

        for video_key in ("3D", "VGA", "Display"):
            for pci_device in lspci_output:
                if video_key in pci_device:
                    gpus_list.append(pci_device.partition(": ")[2])

        return gpus_list

    def output(self, output) -> None:
        if not self.value:
            output.append(self.name, self._default_strings.get("not_detected"))
            return

        if self.options.get("one_line"):
            output.append(self.name, ", ".join(self.value))
        else:
            for gpu_device in self.value:
                output.append(self.name, gpu_device)
