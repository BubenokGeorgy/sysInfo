import os
import platform
from subprocess import DEVNULL, CalledProcessError, check_output
from typing import Optional

from entry import Entry


class Model(Entry):

    LINUX_DMI_SYS_PATH = "/sys/devices/virtual/dmi/id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if platform.system() == "Linux":
            virtual_env_info = self._fetch_virtual_env_info()
            model_name = self._fetch_dmi_info()
            if virtual_env_info is not None:
                model_name = model_name or self._default_strings.get("virtual_environment")
                self.value = f"{model_name} ({virtual_env_info})"
            elif model_name:
                self.value = model_name

    def _fetch_virtual_env_info(self) -> Optional[str]:
        try:
            return check_output(
                "systemd-detect-virt", stderr=DEVNULL, universal_newlines=True
            ).rstrip()
        except CalledProcessError:
            return None
        except FileNotFoundError:
            try:
                return (
                    ", ".join(
                        check_output(
                            "virt-what",
                            stderr=DEVNULL,
                            universal_newlines=True,
                        ).splitlines()
                    )
                    or None
                )
            except (OSError, CalledProcessError):
                return None

    @classmethod
    def _fetch_dmi_info(cls) -> Optional[str]:

        def _read_dmi_file(file_name: str) -> str:
            try:
                with open(
                    os.path.join(cls.LINUX_DMI_SYS_PATH, file_name), encoding="UTF-8"
                ) as f_dmi_file:
                    dmi_info = f_dmi_file.read().rstrip()
            except OSError:
                return ""

            if "to be filled" in dmi_info.lower():
                return ""

            return dmi_info

        product_name = _read_dmi_file("product_name")
        if product_name:
            product_info = [product_name]
            sys_vendor = _read_dmi_file("sys_vendor")
            if sys_vendor and not product_name.startswith(sys_vendor):
                product_info.insert(0, sys_vendor)
            product_info.append(_read_dmi_file("product_version"))
            return " ".join(filter(None, product_info))

        board_name = _read_dmi_file("board_name")
        if board_name:
            board_info = [board_name]
            board_info.insert(0, _read_dmi_file("board_vendor"))
            board_info.append(_read_dmi_file("board_version"))

            return " ".join(filter(None, board_info))

        return None
