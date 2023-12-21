import re
import sys
from bisect import bisect
from enum import Enum

from environment import Environment

ANSI_ECMA_REGEXP = re.compile(r"\x1b\[\d+(?:(?:;\d+)+)?m")


class Style:

    def __str__(self):
        if self.should_color_output():
            return self.escape_code_from_attrs(";".join(map(str, self.value)))
        return ""

    @staticmethod
    def should_color_output() -> bool:

        if Environment.CLICOLOR_FORCE:
            return True

        if Environment.NO_COLOR:
            return False

        return sys.stdout.isatty() and Environment.CLICOLOR

    @staticmethod
    def remove_colors(string: str) -> str:
        return ANSI_ECMA_REGEXP.sub("", string)

    @classmethod
    def escape_code_from_attrs(cls, display_attrs: str) -> str:
        return f"\x1b[{display_attrs}m"


class Colors(Style, Enum):
    CLEAR = (0,)
    RED_NORMAL = (0, 31)
    RED_BRIGHT = (1, 31)
    GREEN_NORMAL = (0, 32)
    GREEN_BRIGHT = (1, 32)
    YELLOW_NORMAL = (0, 33)
    YELLOW_BRIGHT = (1, 33)
    BLUE_NORMAL = (0, 34)
    BLUE_BRIGHT = (1, 34)
    MAGENTA_NORMAL = (0, 35)
    MAGENTA_BRIGHT = (1, 35)
    CYAN_NORMAL = (0, 36)
    CYAN_BRIGHT = (1, 36)
    WHITE_NORMAL = (0, 37)
    WHITE_BRIGHT = (1, 37)

    def __str__(self):
        return super().__str__()

    def __format__(self, _):
        return super().__str__()

    @staticmethod
    def get_level_color(value: float, yellow_bpt: float, red_bpt: float) -> "Colors":
        level_colors = (Colors.GREEN_NORMAL, Colors.YELLOW_NORMAL, Colors.RED_NORMAL)
        return level_colors[bisect((yellow_bpt, red_bpt), value)]
