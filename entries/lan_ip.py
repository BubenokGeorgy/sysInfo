import ipaddress
from itertools import islice
from typing import Iterator

try:
    import netifaces
except ImportError:
    netifaces = None

from entry import Entry


class LanIP(Entry):

    _PRETTY_NAME = "LAN IP"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not netifaces:
            self._logger.warning(
                "`netifaces` Python module couldn't be found. "
                "Please either install it or explicitly disable `LAN_IP` entry in configuration."
            )
            return

        addr_families = [netifaces.AF_INET]
        if self.options.get("ipv6_support", True):
            addr_families.append(netifaces.AF_INET6)

        max_count = self.options.get("max_count", 4)
        if max_count is False:
            max_count = None

        self.value = list(
            islice(
                self._lan_ip_addresses_generator(addr_families),
                max_count,
            )
        )

    @staticmethod
    def _lan_ip_addresses_generator(
        addr_families: list
    ) -> Iterator[str]:
        for if_name in netifaces.interfaces():
            if_addrs = netifaces.ifaddresses(if_name)
            for addr_family in addr_families:
                for if_addr in if_addrs.get(addr_family, []):
                    ip_addr = ipaddress.ip_address(if_addr["addr"].split("%")[0])

                    if (
                        not ip_addr.is_loopback
                    ):
                        yield ip_addr.compressed

    def output(self, output) -> None:
        if self.value:
            if not self.options.get("one_line", False):
                for ip_address in self.value:
                    output.append(self.name, ip_address)
                return

            text_output = ", ".join(self.value)
        elif netifaces:
            text_output = self._default_strings.get("no_address")
        else:
            text_output = self._default_strings.get("not_detected")

        output.append(self.name, text_output)
