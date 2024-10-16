from datetime import datetime, timedelta

POPULATION_SIZE = 50
NUMB_OF_ELITE_SCHEDULES = 1
TOURNAMENT_SELECTION_SIZE = 1
MUTATION_RATE = 0.1
GENERATIONS = 2000
UNIVERSITY_START_TIME = datetime.strptime("08:30", "%H:%M")
UNIVERSITY_END_TIME = datetime.strptime("16:45", "%H:%M")
LUNCH_BREAK_START = datetime.strptime("12:45", "%H:%M")
LUNCH_BREAK_END = datetime.strptime("13:30", "%H:%M")
TIME_SLOT_DURATION = timedelta(hours=1)
LAB_TIME_SLOT_DURATION = timedelta(hours=2)
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
BREAKONE_START_TIME = datetime.strptime("10:30", "%H:%M")
BREAKONE_END_TIME = datetime.strptime("10:45", "%H:%M")
BREAKTWO_START_TIME = datetime.strptime("15:30", "%H:%M")
BREAKTWO_END_TIME = datetime.strptime("15:45", "%H:%M")
