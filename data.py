import streamlit as st
from prettytable import PrettyTable
from schedule import ClassTimeInfo, Schedule


# Function to extract day and time for sorting
def sort_key(item: ClassTimeInfo) -> tuple[int, int, int, str]:
    # Define the actual order of days
    day_order: dict[str, int] = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }
    day, time, duration = item.class_time.split(" ")
    hours, minutes = map(int, time.split(":"))
    return day_order[day], hours, minutes, duration


def tabulate_schedule(schedule: Schedule) -> None:
    table: PrettyTable = PrettyTable(
        field_names=[
            "Panel",
            "Batch",
            "Department",
            "Course",
            "Room",
            "Professor",
            "Class Time",
        ]
    )
    schedule.classes.sort(key=sort_key)
    for cls in schedule.classes:
        table.add_row(
            row=[
                cls.panel,
                cls.batch,
                cls.department,
                cls.course,
                cls.room,
                cls.professor,
                cls.class_time,
            ]
        )
    st.text(body=table)
