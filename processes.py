import logging
import typing
from subprocess import PIPE, CalledProcessError, check_output

from singleton import Singleton


class Processes(metaclass=Singleton):
    def __init__(self):
        self._processes: typing.List[str]

        try:
            ps_output = check_output(["ps", "-eo", "comm"], stderr=PIPE, universal_newlines=True)
        except FileNotFoundError:
            self._processes = []
            logging.warning("`procps` (or `procps-ng`) couldn't be found on your system.")
        except CalledProcessError as process_error:
            self._processes = []
            logging.warning(
                "This implementation of `ps` might not be supported : %s", process_error.stderr
            )
        else:
            self._processes = ps_output.splitlines()[1:]

    @property
    def list(self) -> tuple:
        return tuple(self._processes)

    @property
    def number(self) -> int:
        return len(self._processes)
