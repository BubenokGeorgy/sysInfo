import json
import logging
import os
from copy import deepcopy
from typing import Any, Dict

from singleton import Singleton
from utility import Utility

DEFAULT_CONFIG: Dict[str, Any] = {
    "allow_overriding": False,
    "parallel_loading": True,
    "suppress_warnings": False,
    "default_strings": {
        "latest": "latest",
        "available": "available",
        "no_address": "No Address",
        "not_detected": "Not detected",
        "virtual_environment": "Virtual Environment",
    },
}


class Configuration(metaclass=Singleton):

    def __init__(self, config_path=None):
        self._config = deepcopy(DEFAULT_CONFIG)
        self._config_files_info = {}
        if config_path:
            self._load_configuration(config_path)
        else:
            self._load_configuration(os.getcwd())

    def get(self, key: str, default=None) -> Any:
        return self._config.get(key, default)

    def get_config_files_info(self) -> Dict[str, os.stat_result]:
        return self._config_files_info.copy()

    def _load_configuration(self, path: str) -> None:
        if not self.get("allow_overriding"):
            return

        if os.path.isdir(path):
            path = os.path.join(path, "config.json")

        try:
            with open(path, mode="rb") as f_config:
                Utility.update_recursive(self._config, json.load(f_config))
                self._config_files_info[path] = os.fstat(f_config.fileno())
        except FileNotFoundError:
            return
        except (PermissionError, json.JSONDecodeError) as error:
            logging.error("%s (%s)", error, path)
            return

        logging.getLogger().setLevel(
            logging.ERROR if self.get("suppress_warnings") else logging.WARN
        )

    def __iter__(self):
        return iter(self._config.items())
