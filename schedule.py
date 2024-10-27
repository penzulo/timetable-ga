from dataclasses import dataclass
from random import choice, randint, sample, shuffle

from constants import (
    DAYS_OF_WEEK,
    LAB_TIME_SLOT_DURATION,
    LUNCH_BREAK_END,
    LUNCH_BREAK_START,
    TIME_SLOT_DURATION,
    UNIVERSITY_END_TIME,
    UNIVERSITY_START_TIME,
)
from models import ClassTime, Course, Department, Panel, Professor, Room


class Data:
    def __init__(self) -> None:
        self._rooms: list[Room] = []
        self._lab_rooms: list[Room] = []
        self._class_times: list[ClassTime] = []
        self._professors: list[Professor] = []
        self._courses: list[Course] = []
        self._depts: list[Department] = []
        self._panels: list[Panel] = []

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
    def panels(self) -> list[Panel]:
        return self._panels

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

    def generate_class_times(self) -> None:
        class_time_id: int = 1
        for day in DAYS_OF_WEEK:
            current_time = UNIVERSITY_START_TIME
            while current_time + LAB_TIME_SLOT_DURATION <= UNIVERSITY_END_TIME:
                if not (LUNCH_BREAK_START <= current_time < LUNCH_BREAK_END):
                    class_time: ClassTime = ClassTime(
                        class_id=f"MT{class_time_id}",
                        day=day,
                        time=current_time.strftime("%H:%M"),
                        duration=TIME_SLOT_DURATION,
                    )
                    self.add_class_time(class_time=class_time)
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

    def assign_professor_availability(self) -> None:
        for professor in self.professors:
            num_available_slots: int = randint(20, 25)
            professor.available_times = sample(self.class_times, num_available_slots)


@dataclass(repr=True)
class ClassTimeInfo:
    panel: str
    batch: str
    department: str
    course: str
    room: str
    professor: str
    class_time: str


class Schedule:
    def __init__(self, data: Data, panel: Panel) -> None:
        self._data: Data = data
        self._panel: Panel = panel
        self._classes: list[ClassTimeInfo] = []
        self._fitness: float = -1
        self._class_numb: int = 0
        self._is_fitness_changed: bool = True

    def __str__(self) -> str:
        return f'Schedule(fitness="{self._fitness}", class_num="{self._class_numb}", fitness_changed={self._is_fitness_changed})'

    def __repr__(self) -> str:
        return f'Schedule(fitness="{self._fitness}", class_num="{self._class_numb}", fitness_changed={self._is_fitness_changed})'

    @property
    def data(self) -> Data:
        return self._data

    @property
    def panel(self) -> Panel:
        return self._panel

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

    def initialize(self) -> "Schedule":
        self._classes.clear()
        available_class_times: list[ClassTime] = self._data.class_times.copy()

        for dept in self._data.departments:
            for course in dept.courses:
                for _ in range(course.lectures_per_week):
                    lecture_class_times: list[ClassTime] = [
                        ct
                        for ct in available_class_times
                        if ct.duration == TIME_SLOT_DURATION
                    ]

                    shuffle(lecture_class_times)
                    if not lecture_class_times:
                        raise ValueError("No available class times for lectures.")

                    lecture_class_time: ClassTime = choice(lecture_class_times)

                    available_professors: list[Professor] = [
                        prof
                        for prof in course.professors
                        if lecture_class_time in prof.available_times
                    ]

                    if not available_professors:
                        print(
                            f"No available professors for {course.name} at {lecture_class_time}\nAttempting another time slot"
                        )
                        continue

                    professor: Professor = choice(available_professors)
                    available_rooms: list[Room] = self._data.rooms.copy()
                    shuffle(available_rooms)
                    room: Room = available_rooms[0]

                    if self._check_conflicts(
                        class_time=lecture_class_time, room=room, professor=professor
                    ):
                        self._classes.append(
                            ClassTimeInfo(
                                panel=self._panel.name,
                                batch="All",
                                department=dept.name,
                                course=course.name,
                                room=room.number,
                                professor=professor.name,
                                class_time=f"{lecture_class_time.day} {lecture_class_time.time} {lecture_class_time.duration}",
                            )
                        )

                        professor.available_times.remove(lecture_class_time)
                        available_class_times.remove(lecture_class_time)

        # Scheduling the labs (updated to avoid double removal of class times)
        for dept in self._data.departments:
            for course in dept.courses:
                for _ in range(course.labs_per_week):
                    lab_class_times: list[ClassTime] = [
                        lt
                        for lt in available_class_times
                        if lt.duration == LAB_TIME_SLOT_DURATION
                    ]
                    shuffle(lab_class_times)

                    if not lab_class_times:
                        raise ValueError("No available class times for labs")
                    lab_class_time: ClassTime = lab_class_times[0]

                    available_lab_professors: list[Professor] = [
                        prof
                        for prof in course.professors
                        if lab_class_time in prof.available_times
                    ]

                    if not available_lab_professors:
                        print(
                            f"No available professors for lab {course.name} at {lab_class_time}\n Attempting another time slot"
                        )
                        continue

                    professor = choice(available_lab_professors)
                    available_lab_rooms: list[Room] = self._data.lab_rooms.copy()

                    if len(available_lab_rooms) < self._panel.num_batches:
                        raise ValueError(
                            f"Not enough lab rooms to schedule labs for all batches in panel {self._panel.name}."
                        )

                    shuffle(available_lab_rooms)

                    # Schedule labs for all batches
                    for batch_num in range(1, self._panel.num_batches + 1):
                        # professor = choice(course.professors)
                        if available_lab_rooms:
                            lab_room: Room = available_lab_rooms.pop()
                        else:
                            raise ValueError(
                                f"Not enough lab rooms for all the batches in panel {self._panel.name}"
                            )

                        if self._check_conflicts(
                            class_time=lab_class_time,
                            room=lab_room,
                            professor=professor,
                        ):
                            self._classes.append(
                                ClassTimeInfo(
                                    panel=self._panel.name,
                                    batch=f"Batch {batch_num}",
                                    department=dept.name,
                                    course=f"{course.name} (Lab)",
                                    room=lab_room.number,
                                    professor=professor.name,
                                    class_time=f"{lab_class_time.day} {lab_class_time.time} ({lab_class_time.duration})",
                                )
                            )

                            # Remove the scheduled time from the professor's available times
                            professor.available_times.remove(lab_class_time)
                        else:
                            # If conflict is detected, return the lab room to available_lab_rooms
                            available_lab_rooms.append(lab_room)

                    # Remove lab class time only once after all batches have been scheduled
                    available_class_times.remove(lab_class_time)

        return self

    def _check_conflicts(
        self, class_time: ClassTime, room: Room, professor: Professor
    ) -> bool:
        # Check if the professor is available at the given time
        if class_time not in professor.available_times:
            return False  # Conflict if the professor is not available at this time.

        for cls in self._classes:
            if (
                cls.class_time
                == f"{class_time.day} {class_time.time} ({class_time.duration})"
            ):
                if cls.room == room.number or cls.professor == professor.name:
                    return False
        return True

    def calculate_fitness(self) -> float:
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
