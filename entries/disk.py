import re
from subprocess import DEVNULL, PIPE, run
from typing import Dict

from colors import Colors
from entry import Entry


class Disk(Entry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._disk_dict = self._get_df_output_dict()
        self.value = self._get_local_filesystems()

    def _get_local_filesystems(self) -> Dict[str, dict]:

        device_path_regexp = re.compile(r"^\/dev\/(?:(?!loop|[rs]?vnd|lofi|dm).)+$")

        disk_dict = self._disk_dict

        local_disk_dict: Dict[str, dict] = {}
        for mount_point, disk_data in disk_dict.items():
            if (
                device_path_regexp.match(disk_data["device_path"])
                and not any(
                    disk_data["device_path"] == present_disk_data["device_path"]
                    for present_disk_data in local_disk_dict.values()
                )
            ):
                local_disk_dict[mount_point] = disk_data
        return local_disk_dict

    @staticmethod
    def _get_df_output_dict() -> Dict[str, dict]:
        try:
            df_output = run(
                ["df", "-P", "-k"],
                env={"LANG": "C"},
                universal_newlines=True,
                stdout=PIPE,
                stderr=DEVNULL,
                check=False,
                encoding="utf-8",
            ).stdout
        except FileNotFoundError:
            return {}

        df_output_dict = {}
        for df_entry_match in re.finditer(
            r"""^(?P<device_path>.+?)\s+
                 (?P<total_blocks>\d+)\s+
                 (?P<used_blocks>\d+)\s+
                 \d+\s+ # avail blocks
                 \d+%\s+ # capacity
                 (?P<mount_point>.*)$""",
            df_output,
            flags=re.MULTILINE | re.VERBOSE,
        ):
            total_blocks = int(df_entry_match.group("total_blocks"))
            if total_blocks == 0:
                continue

            df_output_dict[df_entry_match.group("mount_point")] = {
                "device_path": df_entry_match.group("device_path"),
                "used_blocks": int(df_entry_match.group("used_blocks")),
                "total_blocks": total_blocks,
            }
        return df_output_dict

    @staticmethod
    def _blocks_to_human_readable(blocks: float, suffix: str = "B") -> str:
        for unit in ("Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi"):
            if blocks < 1024.0:
                break

            blocks /= 1024.0

        return f"{blocks:02.1f} {unit}{suffix}"

    def output(self, output) -> None:
        filesystems = self.value

        if not filesystems:
            super().output(output)
            return

        name = self.name
        filesystems = {
            None: {
                "device_path": None,
                "used_blocks": sum(
                    filesystem_data["used_blocks"] for filesystem_data in filesystems.values()
                ),
                "total_blocks": sum(
                     filesystem_data["total_blocks"] for filesystem_data in filesystems.values()
                  ),
              }
        }

        for mount_point, filesystem_data in filesystems.items():
            level_color = Colors.get_level_color(
                (filesystem_data["used_blocks"] / filesystem_data["total_blocks"]) * 100,
                self.options.get("warning_use_percent", 50),
                self.options.get("danger_use_percent", 75),
            )

            pretty_filesystem_value = f"{level_color}{{}}{Colors.CLEAR} / {{}}".format(
                self._blocks_to_human_readable(filesystem_data["used_blocks"]),
                self._blocks_to_human_readable(filesystem_data["total_blocks"]),
            )
            output.append(name, pretty_filesystem_value)
