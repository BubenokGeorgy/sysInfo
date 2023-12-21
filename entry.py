import logging
from abc import ABC as AbstractBaseClass
from abc import abstractmethod
from typing import Optional

from configuration import Configuration


class Entry(AbstractBaseClass):

    _PRETTY_NAME: Optional[str] = None

    def __new__(cls, *_, **kwargs):
        return super().__new__(cls)

    @abstractmethod
    def __init__(self, name: Optional[str] = None, value=None, options: Optional[dict] = None):
        self.name = name or self._PRETTY_NAME or self.__class__.__name__
        self.value = value
        self.options = options or {}
        self._default_strings = Configuration().get("default_strings")
        self._logger = logging.getLogger(self.__module__)

    def output(self, output) -> None:
        if self.value:
            output.append(self.name, str(self.value))
        else:
            output.append(self.name, self._default_strings.get("not_detected"))
