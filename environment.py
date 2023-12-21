import os

from singleton import Singleton


class Environment(metaclass=Singleton):

    NO_COLOR = "NO_COLOR" in os.environ
    CLICOLOR = os.getenv("CLICOLOR") != "0"
    CLICOLOR_FORCE = os.getenv("CLICOLOR_FORCE", "0") != "0"
    DO_NOT_TRACK = os.getenv("DO_NOT_TRACK") == "1"

