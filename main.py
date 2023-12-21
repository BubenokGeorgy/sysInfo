import argparse
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from enum import Enum
from typing import Callable, Optional

from _version import __version__
from configuration import Configuration
from entries.cpu import CPU as e_CPU
from entries.desktop_environment import DesktopEnvironment as e_DesktopEnvironment
from entries.disk import Disk as e_Disk
from entries.distro import Distro as e_Distro
from entries.gpu import GPU as e_GPU
from entries.hostname import Hostname as e_Hostname
from entries.kernel import Kernel as e_Kernel
from entries.lan_ip import LanIP as e_LanIP
from entries.load_average import LoadAverage as e_LoadAverage
from entries.model import Model as e_Model
from entries.packages import Packages as e_Packages
from entries.processes import Processes as e_Processes
from entries.ram import RAM as e_RAM
from entries.shell import Shell as e_Shell
from entries.temperature import Temperature as e_Temperature
from entries.terminal import Terminal as e_Terminal
from entries.uptime import Uptime as e_Uptime
from entries.user import User as e_User
from entries.wan_ip import WanIP as e_WanIP
from entries.window_manager import WindowManager as e_WindowManager
from entry import Entry
from environment import Environment
from output import Output
from processes import Processes


class Entries(Enum):
    User = e_User
    Hostname = e_Hostname
    Model = e_Model
    Distro = e_Distro
    Kernel = e_Kernel
    Uptime = e_Uptime
    LoadAverage = e_LoadAverage
    Processes = e_Processes
    WindowManager = e_WindowManager
    DesktopEnvironment = e_DesktopEnvironment
    Shell = e_Shell
    Terminal = e_Terminal
    Packages = e_Packages
    Temperature = e_Temperature
    CPU = e_CPU
    GPU = e_GPU
    RAM = e_RAM
    Disk = e_Disk
    LAN_IP = e_LanIP
    WAN_IP = e_WanIP


def args_parsing() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config-path",
        metavar="PATH",
        help="path to a configuration file, or a directory containing a `config.json`",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="count",
        help="output entries data to JSON format, use multiple times to increase indentation",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )
    return parser.parse_args()


def main():
    args = args_parsing()

    logging.basicConfig(format="%(levelname)s: [%(name)s] %(message)s")

    Processes()
    Environment()
    configuration = Configuration(config_path=args.config_path)

    available_entries = [
        {"type": entry_name}
        for entry_name in Entries.__members__
    ]
    output = Output(
        format_to_json=args.json,
    )

    def _entry_instantiator(entry: dict) -> Optional[Entry]:
        try:
            return Entries[entry.pop("type")].value(
                options=entry,
            )
        except KeyError as key_error:
            logging.warning("One entry (misses or) uses an invalid `type` field (%s).", key_error)
            return None

    with ExitStack() as cm_stack:
        mapper: Callable

        if not configuration.get("parallel_loading"):
            mapper = map
        else:
            executor = cm_stack.enter_context(
                ThreadPoolExecutor(
                    max_workers=min(len(available_entries) or 1, (os.cpu_count() or 1) + 4)
                )
            )
            mapper = executor.map

        for entry_instance in mapper(_entry_instantiator, available_entries):
            if entry_instance:
                output.add_entry(entry_instance)

    output.output()


main()
