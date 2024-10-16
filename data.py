from schedule import Schedule
from prettytable import PrettyTable
import streamlit as st


def tabulate_schedule(schedule: Schedule) -> None:
    table: PrettyTable = PrettyTable(
        [
            "Panel",
            "Batch",
            "Department",
            "Course",
            "Room",
            "Professor",
            "Class Time",
        ]
    )
    for cls in schedule.get_classes():
        table.add_row(
            [
                cls["panel"],
                cls["batch"],
                cls["department"],
                cls["course"],
                cls["room"],
                cls["professor"],
                cls["class_time"],
            ]
        )
    st.text(table)
