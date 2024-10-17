import streamlit as st
from prettytable import PrettyTable

from schedule import Schedule


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
    for cls in schedule.get_classes():
        table.add_row(
            row=[
                cls["panel"],
                cls["batch"],
                cls["department"],
                cls["course"],
                cls["room"],
                cls["professor"],
                cls["class_time"],
            ]
        )
    st.text(body=table)
