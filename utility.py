from typing import Tuple
from singleton import Singleton


class Utility(metaclass=Singleton):

    @classmethod
    def update_recursive(cls, old_dict: dict, new_dict: dict) -> None:
        for key, value in new_dict.items():
            if key in old_dict and isinstance(old_dict[key], dict) and isinstance(value, dict):
                cls.update_recursive(old_dict[key], value)
            else:
                old_dict[key] = value

    @staticmethod
    def version_to_semver_segments(version: str) -> Tuple[int, ...]:
        return tuple(map(int, version.partition("-")[0].split(".")))
