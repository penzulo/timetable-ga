from datetime import datetime
from json import load
from typing import Any, Callable, Dict, Iterable, List, Set

from prettytable import PrettyTable

from models import (
    Course,
    Department,
    Division,
    Professor,
    Room,
    ScheduledClass,
    TimeSlot,
)
from schedule import ScheduleOptimizer

TimeSlots = List[TimeSlot]
ScheduledClasses = List[ScheduledClass]
Rooms = List[Room]
Departments = List[Department]
DivisionSet = Set[Division]
Professors = List[Professor]

# Callable Types
RegisterFunc = Callable[[Any], None]

# Define the custom weekday order
weekday_order: Dict[str, int] = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
}


def sort_and_display(schedule: ScheduleOptimizer) -> PrettyTable:
    sorted_schedule: List[ScheduledClass] = sorted(
        schedule.raw_schedule, key=lambda sched: sched.time_slot.slot_id
    )

    table = PrettyTable()
    table.field_names = [
        "Day",
        "Start Time",
        "End Time",
        "Course Title",
        "Professor",
        "Room",
        "Division",
        "Batch",
        "Department",
    ]

    for entry in sorted_schedule:
        table.add_row(
            [
                entry.time_slot.day,
                f"{entry.time_slot.start:%H:%M}",
                f"{(entry.time_slot.start + entry.time_slot.duration):%H:%M}",
                entry.course.title,
                f"Dr. {entry.professor.name}",
                entry.room.number,
                entry.division.name,
                entry.batch,
                entry.department.department_name,
            ]
        )

    return table


def load_data() -> ScheduleOptimizer:
    def create_rooms(room_sequence: List[Dict[str, Any]]) -> Rooms:
        return [Room(room["room_number"]) for room in room_sequence]

    def create_professors(professor_sequence: List[Dict[str, Any]]) -> Professors:
        return [
            Professor(
                name=prof["name"],
                available_start=datetime.strptime(prof["available"]["start"], "%H:%M"),
                available_end=datetime.strptime(prof["available"]["end"], "%H:%M"),
            )
            for prof in professor_sequence
        ]

    def create_departments(dept_sequence: List[Dict[str, Any]]) -> Departments:
        depts: Departments = []
        for dept in dept_sequence:
            department = Department(
                dept["department_name"],
                courses=[
                    Course(
                        title=course["title"],
                        weekly_lectures=course["weekly_lectures"],
                        weekly_labs=course["weekly_labs"],
                    )
                    for course in dept["offered_courses"]
                ],
            )
            depts.append(department)

        return depts

    def assign_professors(depts: Departments, professors: Professors) -> None:
        prof_count: int = len(professors)
        lab_prof_index: int = prof_count // 2
        prof_index: int = 0

        for dept in depts:
            for course in dept.offered_courses:
                course.assign_professor(professors[prof_index])
                prof_index = (prof_index + 1) % prof_count

                if course.weekly_labs > 0:
                    course.assign_lab_professor(professors[lab_prof_index])
                    lab_prof_index = (lab_prof_index + 1) % prof_count

    with open("input.json", "r") as f:
        data = load(f)

    rooms = create_rooms(data["rooms"])
    lab_rooms = create_rooms(data["lab_rooms"])
    professors = create_professors(data["professors"])
    departments = create_departments(data["departments"])
    assign_professors(depts=departments, professors=professors)

    divisions: DivisionSet = {
        Division(name=div["name"], num_batches=div["num_batches"])
        for div in data["divisions"]
    }

    def register_entity(
        entity_list: Iterable[Any], register_func: RegisterFunc
    ) -> None:
        for entity in entity_list:
            try:
                register_func(entity)
            except ValueError:
                continue

    default_schedule = ScheduleOptimizer()
    register_entity(rooms, default_schedule.register_room)
    register_entity(lab_rooms, default_schedule.register_lab_room)
    register_entity(departments, default_schedule.register_department)
    register_entity(divisions, default_schedule.register_division)
    return default_schedule
