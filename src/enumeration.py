from enum import Enum

class TimeFlag(Enum):
    ALL = 1
    MONTH = 2
    WEEK = 3
    DAY = 4

class HallOfFame(Enum):
    catches = 1
    legendary = 2
    mythical = 3
    ultrabeast = 4
    shiny = 5