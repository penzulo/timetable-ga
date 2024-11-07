from dataclasses import dataclass
from random import choice
from time import strptime
from typing import Optional

from constants import (
    DAYS_OF_WEEK,
    LAB_TIME_SLOT_DURATION,
    LUNCH_BREAK_END,
    LUNCH_BREAK_START,
    TIME_SLOT_DURATION,
    UNIVERSITY_END_TIME,
    UNIVERSITY_START_TIME,
)
from models import ClassTime, Course, Department, Division, Professor, Room


class Data:
    """This class represents the data model for the scheduling system. 
    It contains properties and methods for managing the various entities involved in the scheduling process, such as rooms, class times, professors, courses, and departments. 
    The `generate_class_times` method is responsible for generating a set of class time slots based on the university's operating hours and lunch break schedule. 
    The `assign_professor_availability` method randomly assigns available time slots to each professor."""
    def __init__(self) -> None:
        self._rooms: list[Room] = []
        self._lab_rooms: list[Room] = []
        self._class_times: list[ClassTime] = []
        self._professors: list[Professor] = []
        self._courses: list[Course] = []
        self._depts: list[Department] = []
        self._divisions: list[Division] = []

    @property
    def rooms(self) -> list[Room]:
        return self._rooms

    @property
    def lab_rooms(self) -> list[Room]:
        return self._lab_rooms

    @property
    def class_times(self) -> list[ClassTime]:
        return self._class_times

    @property
    def professors(self) -> list[Professor]:
        return self._professors

    @property
    def courses(self) -> list[Course]:
        return self._courses

    @property
    def departments(self) -> list[Department]:
        return self._depts

    @property
    def divisions(self) -> list[Division]:
        return self._divisions

    def add_room(self, room: Room) -> None:
        self._rooms.append(room)

    def add_lab_room(self, room: Room) -> None:
        self._lab_rooms.append(room)

    def add_class_time(self, class_time: ClassTime) -> None:
        self._class_times.append(class_time)

    def add_professor(self, professor: Professor) -> None:
        self._professors.append(professor)

    def add_course(self, course: Course) -> None:
        self._courses.append(course)

    def add_dept(self, dept: Department) -> None:
        self._depts.append(dept)

    def add_division(self, panel: Division) -> None:
        self._divisions.append(panel)

    def generate_class_times(self) -> None:
        class_time_id: int = 1
        for day in DAYS_OF_WEEK:
            current_time = UNIVERSITY_START_TIME
            while current_time + LAB_TIME_SLOT_DURATION <= UNIVERSITY_END_TIME:
                if not (LUNCH_BREAK_START <= current_time < LUNCH_BREAK_END):
                    self.add_class_time(class_time=ClassTime(
                        class_id=f"MT{class_time_id}",
                        day=day,
                        time=current_time.strftime("%H:%M"),
                        duration=TIME_SLOT_DURATION,
                    ))
                    class_time_id += 1
                    if current_time + LAB_TIME_SLOT_DURATION <= UNIVERSITY_END_TIME:
                        lab_time: ClassTime = ClassTime(
                            class_id=f"MT{class_time_id}",
                            day=day,
                            time=current_time.strftime("%H:%M"),
                            duration=LAB_TIME_SLOT_DURATION,
                        )
                        self.add_class_time(class_time=lab_time)
                        class_time_id += 1
                current_time += TIME_SLOT_DURATION


@dataclass(repr=True)
class ClassTimeInfo:
    division: str
    batch: str
    department: str
    course: str
    room: str
    professor: str
    class_time: str


class Schedule:
    def __init__(self, data: Data, division: Division) -> None:
        self._data: Data = data
        self._division: Division = division 
        self._classes: list[ClassTimeInfo] = []
        self._fitness: float = -1
        self._class_numb: int = 0
        self._is_fitness_changed: bool = True

    def __repr__(self) -> str:
        return f'Schedule(fitness="{self._fitness}", class_num="{self._class_numb}", fitness_changed={self._is_fitness_changed})'

    @property
    def data(self) -> Data:
        return self._data

    @property
    def division(self) -> Division:
        return self._division

    @property
    def classes(self) -> list[ClassTimeInfo]:
        self._is_fitness_changed = True
        return self._classes

    @property
    def fitness(self) -> float:
        if self._is_fitness_changed:
            self._fitness = self.calculate_fitness()
            self._is_fitness_changed = False
        return self._fitness

    def generate_schedule(self) -> "Schedule":
        self._classes.clear()
        for dept in self._data.departments:
            for course in dept.courses:
                for division in self._data.divisions:
                    for _ in range(course.lectures_per_week):
                        lecture_class_times: list[ClassTime] = [ct for ct in self._data.class_times if ct.duration == TIME_SLOT_DURATION]
                        random_lecture_time: Optional[ClassTime] = choice(lecture_class_times) if lecture_class_times else None

                        available_professors: list[Professor] = [prof for prof in course.professors if not prof.is_booked(random_lecture_time)]
                        random_professor: Optional[Professor] = choice(available_professors) if available_professors else None

                        available_rooms: list[Room] = [room for room in self._data.rooms if not room.is_booked(random_lecture_time)]
                        random_room: Room = choice(available_rooms) if available_rooms else None

                        if not self._is_conflicting(class_time=random_lecture_time, room=random_room, professor=random_professor):
                            random_room.book_room(random_lecture_time)
                            random_professor.book_professor(random_lecture_time)
                            self._classes.append(ClassTimeInfo(
                                    division=self._division.name,
                                    batch=f"All",
                                    department=dept.name,
                                    course=course.name,
                                    room=random_room.number,
                                    professor=random_professor.name,
                                    class_time=f"{random_lecture_time.day} {random_lecture_time.time} ({random_lecture_time.duration})",
                            ))

                    for _ in range(course.labs_per_week):
                        for batch in range(1, division.num_batches + 1):
                            lab_class_times: list[ClassTime] = [lt for lt in self._data.class_times if lt.duration == LAB_TIME_SLOT_DURATION]
                            random_lab_time: Optional[ClassTime] = choice(lab_class_times) if lab_class_times else None

                            available_professors = [prof for prof in course.professors if random_lab_time not in prof.booked_times]
                            random_professor: Optional[Professor] = choice(available_professors) if available_professors else None

                            available_rooms = [room for room in self._data.rooms if random_lab_time not in room.booked_times]
                            random_room = choice(available_rooms) if available_rooms else None

                            if not self._is_conflicting(class_time=random_lab_time, room=random_room, professor=random_professor):
                                random_room.book_room(random_lab_time)
                                random_professor.book_professor(random_lab_time)

                                self._classes.append(ClassTimeInfo(
                                    division=self._division.name,
                                    batch=f"Batch {batch}",
                                    department=dept.name,
                                    course=f"{course.name} (Lab)",
                                    room=random_room.number,
                                    professor=random_professor.name,
                                    class_time=f"{random_lab_time.day} {random_lab_time.time} ({random_lab_time.duration})",
                                ))
        return self

    def _is_conflicting(
        self, class_time: Optional[ClassTime], room: Optional[Room], professor: Optional[Professor]
    ) -> bool:
        if class_time is None or room is None or professor is None:
            return True # Either a room, a lecture time or the professor is not available

        # Logic for checking overlapping of classes
        for cls in self._classes:
            le_or_la_time = strptime(cls.class_time.split(" ")[-1].strip("()"), "%H:%M")
            if self._classes.index(le_or_la_time) != len(self._classes):
                next_le_or_la_time = strptime(self._classes[self._classes.index(cls) + 1], "%H:%M")
                if le_or_la_time + class_time.time > next_le_or_la_time:
                    return False

            # This code isn't really necessary -
            # if (
            #     cls.class_time
            #     == f"{class_time.day} {class_time.time} ({class_time.duration})"
            # ):
            #     if cls.room == room.number or cls.professor == professor.name:
            #         return True
            # As we check for available rooms and professors before their allotment.
            # We don't schedule a class if there are no - professors, rooms or class times available.
            # So there is no point in checking for conflicts if such classes are never scheduled.
        return False

    def calculate_fitness(self) -> float:
        # This function contains bad programming logic as the fitness will always be 1 if we only schedule classes if there are 0 conflicts.
        conflicts: int = 0
        classes: list[ClassTimeInfo] = self.classes
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                class_a: ClassTimeInfo = classes[i]
                class_b: ClassTimeInfo = classes[j]
                if class_a.class_time == class_b.class_time:
                    if class_a.room == class_b.room:
                        conflicts += 1
                    if class_a.professor == class_b.professor:
                        conflicts += 1
                    if class_a.batch == class_b.batch and class_a.batch != "All":
                        conflicts += 1
        return 1 / (1 + conflicts)
