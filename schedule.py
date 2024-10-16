from constants import (
    TIME_SLOT_DURATION,
    LAB_TIME_SLOT_DURATION,
    DAYS_OF_WEEK,
    UNIVERSITY_END_TIME,
    UNIVERSITY_START_TIME,
    LUNCH_BREAK_END,
    LUNCH_BREAK_START,
)
from random import shuffle, choice
from typing import Optional
from models import ClassTime, Room, Professor, Course, Department, Panel


class Data:
    def __init__(self) -> None:
        self._rooms: list[Room] = []
        self._lab_rooms: list[Room] = []
        self._class_times: list[ClassTime] = []
        self._professors: list[Professor] = []
        self._courses: list[Course] = []
        self._depts: list[Department] = []
        self._panels: list[Panel] = []

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

    def add_panel(self, panel: Panel) -> None:
        self._panels.append(panel)

    def get_rooms(self) -> list[Room]:
        return self._rooms

    def get_lab_rooms(self) -> list[Room]:
        return self._lab_rooms

    def get_class_times(self) -> list[ClassTime]:
        return self._class_times

    def get_professors(self) -> list[Professor]:
        return self._professors

    def get_courses(self) -> list[Course]:
        return self._courses

    def get_depts(self) -> list[Department]:
        return self._depts

    def get_panels(self) -> list[Panel]:
        return self._panels

    def generate_class_times(self) -> None:
        class_time_id: int = 1
        for day in DAYS_OF_WEEK:
            current_time = UNIVERSITY_START_TIME
            while current_time + LAB_TIME_SLOT_DURATION <= UNIVERSITY_END_TIME:
                if not (LUNCH_BREAK_START <= current_time < LUNCH_BREAK_END):
                    class_time = ClassTime(
                        id=f"MT{class_time_id}",
                        day=day,
                        time=current_time.strftime("%H:%M"),
                        duration=TIME_SLOT_DURATION,
                    )
                    self.add_class_time(class_time)
                    class_time_id += 1
                    if current_time + LAB_TIME_SLOT_DURATION <= UNIVERSITY_END_TIME:
                        lab_time = ClassTime(
                            id=f"MT{class_time_id}",
                            day=day,
                            time=current_time.strftime("%H:%M"),
                            duration=LAB_TIME_SLOT_DURATION,
                        )
                        self.add_class_time(lab_time)
                        class_time_id += 1
                current_time += TIME_SLOT_DURATION


class Schedule:
    def __init__(self, data: Data, panel: Panel) -> None:
        self._data: Data = data
        self._panel: Panel = panel
        self._classes: list[ClassTime] = []
        self._fitness: float = -1
        self._class_numb: int = 0
        self._is_fitness_changed: bool = True

    def get_classes(self) -> list[ClassTime]:
        self._is_fitness_changed = True
        return self._classes

    def initialize(self) -> "Schedule":
        self._classes: list[dict[str, str | int]] = []
        available_class_times = self._data.get_class_times().copy()

        for dept in self._data.get_depts():
            for course in dept.get_courses():
                for _ in range(course.get_lectures_per_week()):
                    lecture_class_times: list[ClassTime] = [
                        mt
                        for mt in available_class_times
                        if mt.get_duration() == TIME_SLOT_DURATION
                    ]
                    shuffle(lecture_class_times)
                    lecture_class_time = lecture_class_times[0]

                    available_rooms = self._data.get_rooms().copy()
                    shuffle(available_rooms)
                    room = available_rooms.pop()

                    professor = (
                        choice(course.get_professors())
                        if course.get_professors()
                        else None
                    )

                    if professor:
                        # Check for conflicts before assigning
                        if self._check_conflicts(lecture_class_time, room, professor):
                            self._classes.append(
                                {
                                    "panel": self._panel.get_name(),
                                    "batch": "All",
                                    "department": dept.get_name(),
                                    "course": course.get_name(),
                                    "room": room.get_number(),
                                    "professor": professor.get_name(),
                                    "class_time": f"{lecture_class_time.get_day()} {lecture_class_time.get_time()} ({lecture_class_time.get_duration()})",
                                }
                            )
                            available_class_times.remove(lecture_class_time)

                # Schedule Labs similarly...
                for _ in range(course.get_labs_per_week()):
                    lab_class_times = [
                        mt
                        for mt in available_class_times
                        if mt.get_duration() == LAB_TIME_SLOT_DURATION
                    ]
                    shuffle(lab_class_times)
                    lab_class_time = lab_class_times[0]

                    available_lab_rooms = self._data.get_lab_rooms().copy()
                    if len(available_lab_rooms) < self._panel.get_num_batches():
                        raise ValueError(
                            f"Not enough lab rooms to schedule labs for all batches in panel {self._panel.get_name()}."
                        )

                    shuffle(available_lab_rooms)
                    for batch_num in range(1, self._panel.get_num_batches() + 1):
                        lab_room = available_lab_rooms.pop()
                        professor = (
                            choice(course.get_professors())
                            if course.get_professors()
                            else None
                        )
                        if professor:
                            if self._check_conflicts(
                                lab_class_time, lab_room, professor
                            ):
                                self._classes.append(
                                    {
                                        "panel": self._panel.get_name(),
                                        "batch": f"Batch {batch_num}",
                                        "department": dept.get_name(),
                                        "course": f"{course.get_name()} (Lab)",
                                        "room": lab_room.get_number(),
                                        "professor": professor.get_name(),
                                        "class_time": f"{lab_class_time.get_day()} {lab_class_time.get_time()} ({lab_class_time.get_duration()})",
                                    }
                                )
                            available_class_times.remove(lab_class_time)

        return self

    def _check_conflicts(
        self, class_time: ClassTime, room: Room, professor: Professor
    ) -> bool:
        for cls in self._classes:
            if (
                cls["class_time"]
                == f"{class_time.get_day()} {class_time.get_time()} ({class_time.get_duration()})"
            ):
                if (
                    cls["room"] == room.get_number()
                    or cls["professor"] == professor.get_name()
                ):
                    return False
        return True

    def get_fitness(self) -> float:
        if self._is_fitness_changed:
            self._fitness = self.calculate_fitness()
            self._is_fitness_changed = False
        return self._fitness

    def calculate_fitness(self) -> float:
        conflicts: int = 0
        classes: list[ClassTime] = self.get_classes()
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                classA: ClassTime = classes[i]
                classB: ClassTime = classes[j]
                if classA["class_time"] == classB["class_time"]:
                    if classA["room"] == classB["room"]:
                        conflicts += 1
                    if classA["professor"] == classB["professor"]:
                        conflicts += 1
                    if classA["batch"] == classB["batch"] and classA["batch"] != "All":
                        conflicts += 1
        return 1 / (1 + conflicts)
