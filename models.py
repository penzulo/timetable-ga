
from dataclasses import dataclass, field
from datetime import timedelta
from secrets import choice
from string import ascii_uppercase, digits
from typing import List, Optional, Set


def generate_id(n: int) -> str:
    return "".join(choice(ascii_uppercase + digits) for _ in range(n))


@dataclass(repr=True, frozen=True)
class TimeSlot:
    slot_id: str
    day: str
    start: str
    end: str
    duration: timedelta


@dataclass(repr=True)
class Professor:
    name: str
    professor_id: Optional[str] = field(default=None)
    available_start: Optional[str] = field(default=None)
    available_end: Optional[str] = field(default=None)
    courses: List["Course"] = field(default_factory=list)
    _reserved_slots: Set[TimeSlot] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.professor_id = generate_id(n=4)

    def is_reserved(self, time_slot: TimeSlot) -> bool:
        return time_slot in self._reserved_slots

    def reserve_professor(self, time_slot: TimeSlot) -> None:
        if self.is_reserved(time_slot):
            raise ValueError(f"Dr. {self.name} is already booked at {time_slot}")
        self._reserved_slots.add(time_slot)

    def assign_course(self, course: "Course", lab: bool = False) -> None:
        if lab:
            if course.lab_professor is None or course.lab_professor == self:
                self.courses.append(course)
                course.lab_professor = self
                return
            raise ValueError(
                f"Lab Session{course.title} is already assigned to Dr. {course.lab_professor.name}"
            )

        if course.assigned_professor is None or course.assigned_professor == self:
            self.courses.append(course)
            course.assigned_professor = self
            return
        raise ValueError(
            f"Course {course.title} is already assigned to Dr. {course.assigned_professor.name}"
        )


@dataclass(repr=True)
class Room:
    number: str
    _reserved_slots: Set[TimeSlot] = field(default_factory=set)

    def is_reserved(self, time_slot: TimeSlot) -> bool:
        return time_slot in self._reserved_slots

    def reserve_room(self, time_slot: TimeSlot) -> None:
        if self.is_reserved(time_slot):
            raise ValueError(f"Room {self.number} is already booked at {time_slot}")
        self._reserved_slots.add(time_slot)


@dataclass(repr=True)
class Course:
    title: str
    weekly_lectures: int
    code: Optional[str] = field(default=None)
    weekly_labs: int = 0
    assigned_professor: Optional[Professor] = field(default=None)
    lab_professor: Optional[Professor] = field(default=None)

    def __post_init__(self) -> None:
        self.code = generate_id(8)

    def assign_professor(self, professor: Professor) -> None:
        if self.assigned_professor is not None and self.assigned_professor != professor:
            raise ValueError(
                f"Course {self.title} is already assigned to Dr. {self.assigned_professor.name}."
            )
        self.assigned_professor = professor
        if self not in professor.courses:
            professor.assign_course(self)

    def assign_lab_professor(self, professor: Professor) -> None:
        if self.lab_professor is not None and self.lab_professor != professor:
            raise ValueError(
                f"Lab sessions of '{self.title}' are already assigned to Dr. {self.lab_professor.name}. Trying to assign to {professor.name}"
            )
        self.lab_professor = professor
        if self not in professor.courses:
            professor.assign_course(self, lab=True)


@dataclass(repr=True)
class Department:
    department_name: str
    offered_courses: List[Course] = field(default_factory=list)


@dataclass(repr=True, frozen=True)
class Division:
    name: str
    num_batches: int


@dataclass(repr=True)
class ScheduledClass:
    division: Division
    batch: str
    department: Department
    course: Course
    room: Room
    professor: Professor
    time_slot: TimeSlot


