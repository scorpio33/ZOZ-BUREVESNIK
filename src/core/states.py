from enum import Enum, auto

class States(Enum):
    START = auto()
    WAITING_FOR_PASSWORD = auto()
    MAIN_MENU = auto()
    SEARCH = auto()
    SETTINGS = auto()
    MAP = auto()
