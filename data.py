from prettytable import PrettyTable

from schedule import ScheduleOptimizer

# Define the custom weekday order
weekday_order = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}


def sort_and_display(schedule: ScheduleOptimizer):
    # Step 1: Sort by weekday order, start time, and end time
    sorted_schedule = sorted(
        schedule.raw_schedule,
        key=lambda x: (
            x.department.department_name,  # Group by department
            x.division.name,  # Group by division
            x.course.title,  # Group by course
            weekday_order[x.time_slot.day],  # Sort by custom weekday order
            x.time_slot.start,  # Sort by start time
            x.time_slot.end,  # Sort by end time
        ),
    )

    # Step 2: Create and display the PrettyTable
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
                entry.time_slot.start,
                entry.time_slot.end,
                entry.course.title,
                f"Dr. {entry.professor.name}",
                entry.room.number,
                entry.division.name,
                entry.batch,
                entry.department.department_name,
            ]
        )

    print(table)
