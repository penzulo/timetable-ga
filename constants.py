from datetime import datetime, timedelta
from typing import List

POPULATION_SIZE: int = 150
NUMB_OF_ELITE_SCHEDULES: int = 1
STAGNANCY_THRESHOLD: int = 20
TOURNAMENT_SELECTION_SIZE: int = 10
MUTATION_RATE: float = 0.01
CROSSOVER_RATE: float = 0.75
GENERATIONS: int = 2000
UNIVERSITY_START_TIME: datetime = datetime.strptime("08:30", "%H:%M")
UNIVERSITY_END_TIME: datetime = datetime.strptime("16:45", "%H:%M")
LUNCH_BREAK_START: datetime = datetime.strptime("12:45", "%H:%M")
LUNCH_BREAK_END: datetime = datetime.strptime("13:30", "%H:%M")
TIME_SLOT_DURATION: timedelta = timedelta(hours=1)
LAB_TIME_SLOT_DURATION: timedelta = timedelta(hours=2)
DAYS_OF_WEEK: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
BREAKONE_START_TIME: datetime = datetime.strptime("10:30", "%H:%M")
BREAKONE_END_TIME: datetime = datetime.strptime("10:45", "%H:%M")
BREAKTWO_START_TIME: datetime = datetime.strptime("15:30", "%H:%M")
BREAKTWO_END_TIME: datetime = datetime.strptime("15:45", "%H:%M")
