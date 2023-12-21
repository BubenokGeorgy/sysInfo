import json
import platform
import re
from glob import iglob
from subprocess import PIPE, CalledProcessError, run
from typing import List, Optional

from entry import Entry


class Temperature(Entry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._temps: List[float] = []

        self._run_sensors(
            self.options.get("sensors_chipsets"), self.options.get("sensors_excluded_subfeatures")
        )

        if not self._temps:
            if platform.system() == "Linux":
                self._poll_thermal_zones()

        if not self._temps:
            return

        self.value = {
            "temperature": float(round(sum(self._temps) / len(self._temps), 1)),
            "max_temperature": float(round(max(self._temps), 1)),
            "unit": "C",
        }

    def _run_sensors(
        self,
        whitelisted_chips: Optional[List[str]] = None,
        excluded_subfeatures: Optional[List[str]] = None,
    ):
        def _get_sensors_output(whitelisted_chip: Optional[str]) -> Optional[str]:
            sensors_args = ["sensors", "-A", "-j"]
            if whitelisted_chip is not None:
                sensors_args.append(whitelisted_chip)

            error_message = None
            try:
                sensors_output = run(
                    sensors_args, universal_newlines=True, stdout=PIPE, stderr=PIPE, check=True
                )
            except FileNotFoundError:
                return None
            except CalledProcessError as called_process_error:
                error_message = called_process_error.stderr
                return None
            else:
                error_message = sensors_output.stderr
            finally:
                if error_message:
                    for line in error_message.splitlines():
                        self._logger.warning("[lm-sensors]: %s", line)

            return sensors_output.stdout

        sensors_outputs = []
        if whitelisted_chips:
            for whitelisted_chip in whitelisted_chips:
                sensors_outputs.append(_get_sensors_output(whitelisted_chip))
        else:
            sensors_outputs.append(_get_sensors_output(None))

        for sensors_output in sensors_outputs:
            if sensors_output is None:
                continue

            try:
                sensors_data = json.loads(sensors_output)
            except json.JSONDecodeError as json_decode_error:
                self._logger.warning(
                    "Couldn't decode JSON from sensors output : %s", json_decode_error
                )
                continue

            for features in sensors_data.values():
                for subfeature_name, subfeature_value in features.items():
                    if excluded_subfeatures and subfeature_name in excluded_subfeatures:
                        continue

                    for name, value in subfeature_value.items():
                        if value != 0.0 and re.match(r"temp\d_input", name):
                            self._temps.append(value)
                            break

    def _poll_thermal_zones(self) -> None:
        for thermal_file in iglob(r"/sys/class/thermal/thermal_zone*/temp"):
            try:
                with open(thermal_file, encoding="ASCII") as file:
                    temp = float(file.read())
            except OSError:
                continue

            if temp != 0.0:
                self._temps.append(temp / 1000)


