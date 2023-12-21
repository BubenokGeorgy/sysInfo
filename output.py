import os
import sys
from shutil import get_terminal_size
from textwrap import TextWrapper
from typing import cast

from api import API
from colors import ANSI_ECMA_REGEXP, Colors, Style
from distributions import Distributions
from entry import Entry
from exceptions import SysInfoException
from logos import get_logo_width, lazy_load_logo_module


class Output:

    __LOGO_RIGHT_PADDING = "   "

    def __init__(self, **kwargs):
        self._format_to_json = kwargs.get("format_to_json")
        self._distribution = Distributions.get_local()
        logo_module = lazy_load_logo_module(self._distribution.value)
        self._logo, self._colors = logo_module.LOGO.copy(), logo_module.COLORS.copy()
        self._entries_color = self._colors[0]
        self._entries = []
        self._results = []

    def add_entry(self, module: Entry) -> None:
        self._entries.append(module)

    def append(self, key: str, value) -> None:
        self._results.append(f"{self._entries_color}{key}:{Colors.CLEAR} {value}")

    def output(self) -> None:
        if self._format_to_json:
            self._output_json()
        else:
            for entry in self._entries:
                entry.output(self)
            self._output_text()

    def _output_json(self) -> None:
        print(API(self._entries).json_serialization(indent=cast(int, self._format_to_json) - 1))

    def _output_text(self) -> None:

        logo_width = get_logo_width(self._logo, len(self._colors))

        height_diff = len(self._logo) - len(self._results)
        if height_diff >= 0:
            self._results[0:0] = [""] * (height_diff // 2)
            self._results.extend([""] * (len(self._logo) - len(self._results)))
        else:
            colored_empty_line = [str(self._colors[0]) + " " * logo_width]
            self._logo[0:0] = colored_empty_line * (-height_diff // 2)
            self._logo.extend(colored_empty_line * (len(self._results) - len(self._logo)))

        if not sys.stdout.isatty():
            text_width = cast(int, float("inf"))
        else:
            text_width = get_terminal_size().columns - logo_width - len(self.__LOGO_RIGHT_PADDING)

        text_wrapper = TextWrapper(
            width=text_width,
            expand_tabs=False,
            replace_whitespace=False,
            drop_whitespace=False,
            break_on_hyphens=False,
            max_lines=1,
            placeholder="...",
        )
        placeholder_length = len(text_wrapper.placeholder)

        for i, entry in enumerate(self._results):
            wrapped_entry = text_wrapper.fill(Style.remove_colors(entry))
            placeholder_offset = (
                placeholder_length if wrapped_entry.endswith(text_wrapper.placeholder) else 0
            )

            for color_match in ANSI_ECMA_REGEXP.finditer(entry):
                match_index = color_match.start()
                if match_index <= len(wrapped_entry) - placeholder_offset:
                    wrapped_entry = (
                            wrapped_entry[:match_index]
                            + color_match.group()
                            + wrapped_entry[match_index:]
                    )

            if placeholder_offset:
                wrapped_entry = (
                        wrapped_entry[:-placeholder_length]
                        + str(Colors.CLEAR)
                        + wrapped_entry[-placeholder_length:]
                )

            self._results[i] = wrapped_entry

        logo_with_entries = os.linesep.join(
            [
                f"{logo_part}{self.__LOGO_RIGHT_PADDING}{entry_part}"
                for logo_part, entry_part in zip(self._logo, self._results)
            ]
        )

        try:
            print(logo_with_entries.format(c=self._colors) + str(Colors.CLEAR))
        except UnicodeError as unicode_error:
            raise SysInfoException(
                """\
Your locale or TTY does not seem to support UTF-8 encoding.
Please disable Unicode within your configuration file.\
"""
            ) from unicode_error
