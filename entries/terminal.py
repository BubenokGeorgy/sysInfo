import os
import re
from typing import Optional

from colors import Colors, Style
from entry import Entry

COLORTERM_DICT = {
    r"kmscon": "KMSCON",
    r"rxvt": "rxvt",
}

TERM_DICT = {
    r"xterm-termite": "Termite",
}

ENV_DICT = {
    "ALACRITTY_LOG": "Alacritty",
    "GNOME_TERMINAL_SCREEN": "GNOME Terminal",
    "GUAKE_TAB_UUID": "Guake",
    "KITTY_WINDOW_ID": "Kitty",
    "KONSOLE_VERSION": "Konsole",
    "MLTERM": "MLTERM",
    "TERMINATOR_UUID": "Terminator",
}


class Terminal(Entry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = self._detect_terminal_emulator()

    def _get_colors_palette(self) -> str:
        character = "\u2588" if self.options.get("use_unicode", True) else "#"

        return " ".join(
            [
                f"{Colors((0, i))}{character}{Colors((1, i))}{character}{Colors.CLEAR}"
                for i in range(37, 30, -1)
            ]
        )

    @staticmethod
    def _detect_terminal_emulator() -> Optional[str]:
        env_term_program = os.getenv("TERM_PROGRAM")
        if env_term_program:
            env_term_program_version = os.getenv("TERM_PROGRAM_VERSION")
            if env_term_program_version:
                env_term_program += f" {env_term_program_version}"

            return env_term_program

        env_colorterm = os.getenv("COLORTERM")
        if env_colorterm:
            for env_value_re, normalized_name in COLORTERM_DICT.items():
                if re.match(env_value_re, env_colorterm):
                    return normalized_name

        env_term = os.getenv("TERM")
        if env_term:
            for env_value_re, normalized_name in TERM_DICT.items():
                if re.match(env_value_re, env_term):
                    return normalized_name

            if not env_term.startswith("xterm"):
                return env_term

        for env_var, normalized_name in ENV_DICT.items():
            if env_var in os.environ:
                return normalized_name

        return env_term

    def output(self, output) -> None:
        text_output = self.value or self._default_strings.get("not_detected")
        if Style.should_color_output():
            text_output += " " + self._get_colors_palette()

        output.append(self.name, text_output)
