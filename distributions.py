from contextlib import suppress
from enum import Enum
from typing import List, Optional

import distro


class Distributions(Enum):

    ALPINE = "alpine"
    ARCH = "arch"
    CENTOS = "centos"
    DEBIAN = "debian"
    KALI = "kali"
    LINUX = "linux"
    LINUXMINT = "linuxmint"
    UBUNTU = "ubuntu"

    @staticmethod
    def get_identifiers() -> List[str]:
        return [d.value for d in Distributions.__members__.values()]

    @staticmethod
    def get_local() -> "Distributions":
        distribution = Distributions._vendor_detection()

        if not distribution:
            return Distributions.LINUX

        return distribution

    @staticmethod
    def _vendor_detection() -> Optional["Distributions"]:

        with suppress(ValueError):
            return Distributions(distro.id())

        for id_like in distro.like().split(" "):
            with suppress(ValueError):
                return Distributions(id_like)

        return None

    @staticmethod
    def get_distro_name(pretty: bool = True) -> Optional[str]:
        return distro.name(pretty=pretty) or None

    @staticmethod
    def get_ansi_color() -> Optional[str]:
        return distro.os_release_attr("ansi_color") or None
