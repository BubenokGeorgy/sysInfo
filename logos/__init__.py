from importlib import import_module
from types import ModuleType
from typing import List


def lazy_load_logo_module(logo_name: str) -> ModuleType:
    return import_module(f"{__name__}.{logo_name}")


def get_logo_width(logo: List[str], nb_colors: int = 8) -> int:
    return len(logo[0].format(c=[""] * nb_colors))
