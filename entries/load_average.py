import os
from contextlib import suppress

from colors import Colors
from entry import Entry


class LoadAverage(Entry):

    _PRETTY_NAME = "Load Average"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with suppress(AttributeError):
            self.value = os.getloadavg()

    def output(self, output) -> None:
        if not self.value:
            super().output(output)
            return

        decimal_places = self.options.get("decimal_places", 2)
        warning_threshold = self.options.get("warning_threshold", 1.0)
        danger_threshold = self.options.get("danger_threshold", 2.0)

        output.append(
            self.name,
            " ".join(
                [
                    str(Colors.get_level_color(load_avg, warning_threshold, danger_threshold))
                    + str(round(load_avg, decimal_places))
                    + str(Colors.CLEAR)
                    for load_avg in self.value
                ]
            ),
        )
