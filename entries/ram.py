import platform
import re
from contextlib import suppress
from subprocess import check_output
from typing import Tuple

from colors import Colors
from entry import Entry


class RAM(Entry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        used, total = self._get_used_total_values()
        if not total:
            return

        self.value = {
            "used": used,
            "total": total,
            "unit": "MiB",
        }

    def _get_used_total_values(self) -> Tuple[float, float]:
        if platform.system() == "Linux":
            with suppress(IndexError, FileNotFoundError):
                return self._run_free_dash_m()

        with suppress(OSError):
            return self._read_proc_meminfo()

        return 0, 0

    @staticmethod
    def _run_free_dash_m() -> Tuple[float, float]:
        memory_usage = "".join(
            filter(
                re.compile(r"Mem").search,
                check_output(
                    ["free", "-m"], env={"LANG": "C"}, universal_newlines=True
                ).splitlines(),
            )
        ).split()

        return float(memory_usage[2]), float(memory_usage[1])

    @staticmethod
    def _read_proc_meminfo() -> Tuple[float, float]:
        with open("/proc/meminfo", encoding="ASCII") as f_mem_info:
            mem_info_lines = f_mem_info.read().splitlines()

        mem_info = {}
        for line in filter(None, mem_info_lines):
            key, value = line.split(":", maxsplit=1)
            mem_info[key] = float(value.strip(" kB")) / 1024

        total = mem_info["MemTotal"]
        used = (
            total
            + mem_info["Shmem"]
            - (
                mem_info["MemFree"]
                + mem_info["Cached"]
                + mem_info["SReclaimable"]
                + mem_info["Buffers"]
            )
        )
        if used < 0:
            used = total - mem_info["MemFree"]

        return used, total

    def output(self, output) -> None:
        if not self.value:
            super().output(output)
            return

        used = self.value["used"]
        total = self.value["total"]
        unit = self.value["unit"]

        level_color = Colors.get_level_color(
            (used / total) * 100,
            self.options.get("warning_use_percent", 33.3),
            self.options.get("danger_use_percent", 66.7),
        )

        output.append(
            self.name, f"{level_color}{int(used)} {unit}{Colors.CLEAR} / {int(total)} {unit}"
        )
