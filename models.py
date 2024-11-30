from datetime import datetime, timedelta
from secrets import choice
from string import ascii_uppercase, digits
from typing import List, Optional

from constants import (
    BREAKONE_END_TIME,
    BREAKONE_START_TIME,
    BREAKTWO_END_TIME,
    BREAKTWO_START_TIME,
    LUNCH_BREAK_END,
    LUNCH_BREAK_START,
)


def generate_id(n: int) -> str:
    return "".join(choice(ascii_uppercase + digits) for _ in range(n))


class TimeSlot:
    def __init__(self, day: str, start: datetime, duration: timedelta) -> None:
        self.slot_id: str = generate_id(n=4)
        self.day: str = day
        self.start: datetime = start
        self.duration: timedelta = duration

    def __repr__(self) -> str:
        return (
            f"TimeSlot("
            f"id={self.slot_id},"
            f"day={self.day},"
            f"start={self.start.strftime('%H:%M')},"
            f"duration={self.duration}"
            f")"
        )


class Professor:
    def __init__(
        self, available_start: datetime, available_end: datetime, name: str
    ) -> None:
        self.name: str = name
        self.professor_id = generate_id(n=4)
        self.available_start: datetime = available_start
        self.available_end: datetime = available_end
        self.courses: List[Course] = []
        self._reserved_slots: List[TimeSlot] = []

    def __repr__(self) -> str:
        return (
            f"Professor("
            f"name='{self.name}',"
            f"available_start='{self.available_start:%H:%M}',"
            f"available_end='{self.available_end:%H:%M}',"
        )

    def is_reserved(self, time_slot: TimeSlot) -> bool:
        return any(
            [
                not self._is_within_availability(time_slot),
                self._overlaps_with_lunch_break(time_slot),
                self._overlaps_with_first_break(time_slot),
                self._overlaps_with_second_break(time_slot),
                time_slot in self._reserved_slots,
            ]
        )

    def reserve_professor(self, time_slot: TimeSlot) -> None:
        if self.is_reserved(time_slot):
            raise ValueError(
                f"Cannot reserve Dr. {self.name} from {time_slot.start} to {time_slot.start + time_slot.duration}"
            )
        self._reserved_slots.append(time_slot)

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

    @staticmethod
    def _overlaps_with_lunch_break(slot: TimeSlot) -> bool:
        return not (
            slot.start + slot.duration <= LUNCH_BREAK_START
            or slot.start >= LUNCH_BREAK_END
        )

    @staticmethod
    def _overlaps_with_first_break(slot: TimeSlot) -> bool:
        return not (
            slot.start + slot.duration <= BREAKONE_START_TIME
            or slot.start >= BREAKONE_END_TIME
        )

    @staticmethod
    def _overlaps_with_second_break(slot: TimeSlot) -> bool:
        return not (
            slot.start + slot.duration <= BREAKTWO_START_TIME
            or slot.start >= BREAKTWO_END_TIME
        )

    def _is_within_availability(self, slot: TimeSlot) -> bool:
        return (
            self.available_start <= slot.start
            and slot.start + slot.duration <= self.available_end
        )


class Room:
    def __init__(self, number: str) -> None:
        self.number: str = number
        self._reserved_slots: List[TimeSlot] = []

    def __repr__(self) -> str:
        return f"Room(number='{self.number}', reserved_slots='{len(self._reserved_slots)}')"

    def is_reserved(self, time_slot: TimeSlot) -> bool:
        return time_slot in self._reserved_slots

    def reserve_room(self, time_slot: TimeSlot) -> None:
        if self.is_reserved(time_slot):
            raise ValueError(f"Room {self.number} is already booked at {time_slot}")
        self._reserved_slots.append(time_slot)


class Course:
    def __init__(
        self,
        title: str,
        weekly_lectures: int,
        weekly_labs: int = 0,
        assigned_professor: Optional[Professor] = None,
        lab_professor: Optional[Professor] = None,
    ) -> None:
        self.title: str = title
        self.code = generate_id(n=8)
        self.weekly_lectures: int = weekly_lectures
        self.weekly_labs: int = weekly_labs
        self.assigned_professor: Optional[Professor] = assigned_professor
        self.lab_professor: Optional[Professor] = lab_professor

    def __repr__(self) -> str:
        return f"Course(title='{self.title}', code='{self.code}')"

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


class Department:
    def __init__(self, name: str, courses: List[Course]) -> None:
        self.department_name: str = name
        self.offered_courses: List[Course] = courses

    def __repr__(self) -> str:
        return (
            f"Department(name='{self.department_name}', courses={self.offered_courses})"
        )


class Division:
    def __init__(self, name: str, num_batches: int) -> None:
        self.name: str = name
        self.num_batches: int = num_batches

    def __repr__(self) -> str:
        return f"Division(name='{self.name}'m batches='{self.num_batches}')"


class ScheduledClass:
    def __init__(
        self,
        div: Division,
        batch: str,
        dept: Department,
        course: Course,
        room: Room,
        prof: Professor,
        time_slot: TimeSlot,
    ) -> None:
        self.division: Division = div
        self.batch: str = batch
        self.department: Department = dept
        self.course: Course = course
        self.room: Room = room
        self.professor: Professor = prof
        self.time_slot: TimeSlot = time_slot

    def __repr__(self) -> str:
        return (
            f"ScheduledClass("
            f"division={self.division!r}, "
            f"batch={self.batch!r}, "
            f"department={self.department!r}, "
            f"course={self.course.title!r}, "
            f"room={self.room.number!r}, "
            f"professor={self.professor.name!r}, "
            f"time_slot={self.time_slot!r}"
            f")"
        )
