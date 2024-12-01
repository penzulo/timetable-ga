from collections import defaultdict
from datetime import datetime
from random import choice
from typing import DefaultDict, List, Optional, Tuple, Set

from constants import (
    DAYS_OF_WEEK,
    LAB_TIME_SLOT_DURATION,
    LUNCH_BREAK_END,
    LUNCH_BREAK_START,
    TIME_SLOT_DURATION,
    UNIVERSITY_END_TIME,
    UNIVERSITY_START_TIME,
)
from models import Course, Department, Division, Room, ScheduledClass, TimeSlot

# Type Aliases
TimeSlots = List[TimeSlot]
ScheduledClasses = List[ScheduledClass]
Rooms = List[Room]
Departments = List[Department]
Divisions = Set[Division]
DefaultConfCounter = DefaultDict[Tuple[str, str], int]
LecConfCounter = DefaultDict[Tuple[str, int], int]
LabConfCounter = DefaultDict[Tuple[str, int], DefaultDict[int, int]]

# Nullable Types
NullableTimeSlot = Optional[TimeSlot]
NullableRoom = Optional[Room]


def create_timeslots() -> TimeSlots:
    populated_time_slots: TimeSlots = []

    for day in DAYS_OF_WEEK:
        current_time: datetime = UNIVERSITY_START_TIME
        while current_time + TIME_SLOT_DURATION <= UNIVERSITY_END_TIME:
            if LUNCH_BREAK_START <= current_time < LUNCH_BREAK_END:
                current_time += TIME_SLOT_DURATION
                continue

            populated_time_slots.append(
                TimeSlot(
                    day=day,
                    start=current_time,
                    duration=TIME_SLOT_DURATION,
                )
            )

            if current_time + LAB_TIME_SLOT_DURATION <= UNIVERSITY_END_TIME:
                populated_time_slots.append(
                    TimeSlot(
                        day=day,
                        start=current_time,
                        duration=LAB_TIME_SLOT_DURATION,
                    )
                )

            current_time += TIME_SLOT_DURATION

    return populated_time_slots


time_slots: TimeSlots = create_timeslots()


class ScheduleOptimizer:
    def __init__(self) -> None:
        self.raw_schedule: ScheduledClasses = []
        self.rooms: Rooms = []
        self.lab_rooms: Rooms = []
        self.departments: Departments = []
        self.divisions: Divisions = set()
        self.fitness: float = -1.0

    def __repr__(self) -> str:
        return f"Schedule Object of fitness: {self.fitness}"

    def register_room(self, new_room: Room) -> None:
        self.rooms.append(new_room)

    def register_lab_room(self, new_room: Room) -> None:
        self.lab_rooms.append(new_room)

    def register_department(self, new_dept: Department) -> None:
        self.departments.append(new_dept)

    def register_division(self, new_division: Division) -> None:
        self.divisions.add(new_division)

    def create_schedule(self) -> "ScheduleOptimizer":
        self.raw_schedule.clear()

        for department in self.departments:
            self._schedule_department(department, self.divisions)

        return self

    def book_and_add_class(
        self,
        div: Division,
        department: Department,
        course: Course,
        time_slot: TimeSlot,
        room: Room,
        batch: Optional[str] = None,
    ) -> None:
        room.reserve_room(time_slot)

        if batch is not None and course.lab_professor is not None:
            course.lab_professor.reserve_professor(time_slot)
            self.raw_schedule.append(
                ScheduledClass(
                    div=div,
                    batch=f"Batch {batch}",
                    dept=department,
                    course=course,
                    time_slot=time_slot,
                    room=room,
                    prof=course.lab_professor,
                )
            )
            return

        if course.assigned_professor is not None:
            course.assigned_professor.reserve_professor(time_slot)
            self.raw_schedule.append(
                ScheduledClass(
                    div=div,
                    batch="All",
                    dept=department,
                    course=course,
                    time_slot=time_slot,
                    room=room,
                    prof=course.assigned_professor,
                )
            )
            return

    def calculate_fitness(self) -> float:
        conflicts = (
            self._check_room_conflicts()
            + self._check_professor_conflicts()
            + self._check_lab_conflicts()
            + self._check_lecture_conflicts()
        )
        max_conflicts = len(self.raw_schedule) * (len(self.raw_schedule) - 1) // 2
        return max(0.0, 1.0 - (conflicts / max_conflicts))

    def _schedule_department(
        self, department: Department, divisions: Divisions
    ) -> None:
        for course in department.offered_courses:
            for division in divisions:
                self._schedule_course_lectures(course, division, department)
                self._schedule_course_labs(course, division, department)

    def _schedule_course_lectures(
        self, course: Course, division: Division, dept: Department
    ) -> None:
        lecture_slots: TimeSlots = [
            slot
            for slot in time_slots
            if slot.duration == TIME_SLOT_DURATION
            and (
                course.assigned_professor is None
                or not course.assigned_professor.is_reserved(slot)
            )
        ]
        if not lecture_slots:
            return

        for _ in range(course.weekly_lectures):
            random_lecture_slot: NullableTimeSlot = self._choose_random_time_slot(
                lecture_slots
            )
            for _ in range(10):
                if (
                    course.assigned_professor is not None
                    and random_lecture_slot is not None
                    and not course.assigned_professor.is_reserved(random_lecture_slot)
                ):
                    break
                random_lecture_slot = self._choose_random_time_slot(lecture_slots)
            else:
                continue  # Skip this iteration and go the next.

            random_room: NullableRoom = self._choose_available_room(random_lecture_slot)

            if random_room is None:
                continue  # Skip iteration

            self.book_and_add_class(
                div=division,
                department=dept,
                course=course,
                time_slot=random_lecture_slot,
                room=random_room,
            )

    def _schedule_course_labs(
        self, course: Course, div: Division, dept: Department
    ) -> None:
        lab_slots: TimeSlots = [
            slot
            for slot in time_slots
            if slot.duration == LAB_TIME_SLOT_DURATION
            and (
                course.lab_professor is None
                or not course.lab_professor.is_reserved(slot)
            )
        ]

        if not lab_slots:
            return

        for _ in range(course.weekly_labs):
            for batch in range(1, div.num_batches + 1):
                random_lab_slot: NullableTimeSlot = self._choose_random_time_slot(
                    lab_slots
                )
                for _ in range(10):
                    if (
                        course.lab_professor is not None
                        and random_lab_slot is not None
                        and not course.lab_professor.is_reserved(random_lab_slot)
                    ):
                        break
                    random_lab_slot = self._choose_random_time_slot(lab_slots)
                else:
                    continue

                random_room: NullableRoom = self._choose_available_room(random_lab_slot)

                if random_room is None:
                    print("Can't find randomized room for scheduling a lab slot.")
                    continue

                self.book_and_add_class(
                    div=div,
                    batch=str(batch),
                    department=dept,
                    time_slot=random_lab_slot,
                    course=course,
                    room=random_room,
                )

    def _choose_available_room(self, time_slot: TimeSlot) -> NullableRoom:
        available_rooms: Rooms = [
            room for room in self.rooms if not room.is_reserved(time_slot)
        ]
        return choice(available_rooms) if available_rooms else None

    @staticmethod
    def _choose_random_time_slot(time_slots: TimeSlots) -> NullableTimeSlot:
        return choice(time_slots) if time_slots else None

    def _check_room_conflicts(self) -> int:
        conflicts: DefaultConfCounter = defaultdict(int)
        for scheduled_class in self.raw_schedule:
            room_time_key = (
                scheduled_class.room.number,
                scheduled_class.time_slot.slot_id,
            )
            conflicts[room_time_key] += 1

        return sum(count - 1 for count in conflicts.values() if count > 1)

    def _check_professor_conflicts(self) -> int:
        conflicts: DefaultConfCounter = defaultdict(int)
        for scheduled_class in self.raw_schedule:
            professor_time_key = (
                scheduled_class.professor.professor_id,
                scheduled_class.time_slot.slot_id,
            )
            conflicts[professor_time_key] += 1

        return sum(count - 1 for count in conflicts.values() if count > 1)

    def _check_lecture_conflicts(self) -> int:
        counts: LecConfCounter = defaultdict(int)
        conflicts: int = 0

        for scheduled_class in self.raw_schedule:
            if scheduled_class.time_slot.duration == TIME_SLOT_DURATION:
                key = (
                    scheduled_class.course.code,
                    scheduled_class.course.weekly_lectures,
                )
                counts[key] += 1

        for course, lectures in counts.items():
            if lectures != course[1]:
                conflicts += abs(lectures - course[1])

        return conflicts

    def _check_lab_conflicts(self) -> int:
        counts: LabConfCounter = defaultdict(lambda: defaultdict(int))
        conflicts: int = 0

        for scheduled_class in self.raw_schedule:
            if scheduled_class.time_slot.duration == LAB_TIME_SLOT_DURATION:
                batch: int = int(scheduled_class.batch.split()[-1])
                key = (scheduled_class.course.code, scheduled_class.course.weekly_labs)
                counts[key][batch] += 1

        for (_, weekly_labs), batch_counts in counts.items():
            for batch, labs in batch_counts.items():
                if labs != weekly_labs:
                    conflicts += abs(labs - weekly_labs)

        return conflicts
