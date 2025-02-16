from enum import Enum, auto

class States(Enum):
    START = auto()
    INITIAL = auto()
    AUTH = auto()
    WAITING_PASSWORD = auto()
    WAITING_DEVELOPER_CODE = auto()
    MAIN_MENU = auto()
    SEARCH = auto()
    SETTINGS = auto()
    MAP = auto()
    HELP_PROJECT = auto()
    ABOUT = auto()
