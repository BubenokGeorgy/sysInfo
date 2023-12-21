import platform
import re
from subprocess import check_output
from typing import Dict, List

from entry import Entry


class CPU(Entry):

    _MODEL_NAME_REGEXP = re.compile(
        r"^model name\s*:\s*(.*)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    _PHYSICAL_ID_REGEXP = re.compile(
        r"^physical id\s*:\s*(\d+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    _THREADS_PER_CORE_REGEXP = re.compile(
        r"^Thread\(s\) per core\s*:\s*(\d+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    _CORES_PER_SOCKET_REGEXP = re.compile(
        r"^Core\(s\) per socket\s*:\s*(\d+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    _SOCKETS_REGEXP = re.compile(
        r"^Socket\(s\)\s*:\s*(\d+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    _CLUSTERS_REGEXP = re.compile(
        r"^Cluster\(s\)\s*:\s*(\d+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    _CORES_PER_CLUSTER_REGEXP = re.compile(
        r"^Core\(s\) per cluster\s*:\s*(\d+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if platform.system() == "Linux":
            self.value = self._parse_proc_cpuinfo()
        if not self.value:
            self.value = self._parse_lscpu_output()

    @classmethod
    def _parse_proc_cpuinfo(cls) -> List[Dict[str, int]]:
        try:
            with open("/proc/cpuinfo", encoding="ASCII") as f_cpu_info:
                cpu_info = f_cpu_info.read()
        except OSError:
            return []

        model_names = cls._MODEL_NAME_REGEXP.findall(cpu_info)
        physical_ids = cls._PHYSICAL_ID_REGEXP.findall(cpu_info)

        cpus_list: List[Dict[str, int]] = []

        for model_name, physical_id in zip(model_names, physical_ids):
            model_name = re.sub(r"\s+", " ", model_name)

            try:
                cpus_list[int(physical_id)][model_name] += 1
            except KeyError:
                cpus_list[int(physical_id)][model_name] = 1
            except IndexError:
                cpus_list.append({model_name: 1})
        return cpus_list

    @classmethod
    def _parse_lscpu_output(cls) -> List[Dict[str, int]]:
        try:
            cpu_info = check_output("lscpu", env={"LANG": "C"}, universal_newlines=True)
        except FileNotFoundError:
            return []

        nb_threads = cls._THREADS_PER_CORE_REGEXP.findall(cpu_info)
        nb_cores = cls._CORES_PER_SOCKET_REGEXP.findall(
            cpu_info
        ) or cls._CORES_PER_CLUSTER_REGEXP.findall(cpu_info)
        nb_slots = cls._SOCKETS_REGEXP.findall(cpu_info) or cls._CLUSTERS_REGEXP.findall(cpu_info)
        model_names = cls._MODEL_NAME_REGEXP.findall(cpu_info)

        cpus_list = []

        for threads, cores, slots, model_name in zip(nb_threads, nb_cores, nb_slots, model_names):
            for _ in range(int(slots)):
                cpus_list.append({re.sub(r"\s+", " ", model_name): int(threads) * int(cores)})

        return cpus_list

    def output(self, output) -> None:
        if not self.value:
            output.append(self.name, self._default_strings.get("not_detected"))
            return

        entries = []
        for cpus in self.value:
            for model_name, cpu_count in cpus.items():
                if cpu_count > 1:
                    entries.append(f"{cpu_count} x {model_name}")
                else:
                    entries.append(model_name)

        if self.options.get("one_line"):
            output.append(self.name, ", ".join(entries))
        else:
            for entry in entries:
                output.append(self.name, entry)
