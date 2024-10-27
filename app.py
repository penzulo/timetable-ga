import streamlit as st
from constants import GENERATIONS, POPULATION_SIZE
from data import tabulate_schedule
from genetic_alg import GeneticAlgorithm, Population
from models import Course, Department, Panel, Professor, Room
from schedule import Data, Schedule


def main() -> None:
    st.title("University Timetable Scheduling")
    st.header("Input Data")

    data: Data = Data()

    room_count: int = st.number_input(
        label="Number of Rooms:", min_value=1, max_value=20, value=5, key="room_count"
    )
    for i in range(room_count):
        room_number: str = st.text_input(
            f"Room {i + 1} Number:", key=f"room_number_{i}"
        )
        data.add_room(Room(room_number=room_number))

    lab_room_count: int = st.number_input(
        label="Number of Lab Rooms:",
        min_value=1,
        max_value=20,
        value=5,
        key="lab_room_count",
    )

    for i in range(lab_room_count):
        lab_room_number: str = st.text_input(
            label=f"Lab Room {i + 1} Number:", key=f"lab_room_number_{i}"
        )
        data.add_lab_room(Room(room_number=lab_room_number))

    data.generate_class_times()

    professor_count: int = st.number_input(
        label="Number of Professors:",
        min_value=1,
        max_value=50,
        value=10,
        key="professor_count",
    )

    for i in range(professor_count):
        professor_name: str = st.text_input(
            f"Professor {i + 1} Name:", key=f"professor_name_{i}"
        )
        data.add_professor(Professor(professor_id=f"I{i + 1}", name=professor_name))

    dept_count: int = st.number_input(
        label="Number of Departments:",
        min_value=1,
        max_value=5,
        value=2,
        key="dept_count",
    )

    for i in range(dept_count):
        dept_name: str = st.text_input(
            f"Department {i + 1} Name:", key=f"dept_name_{i}"
        )
        course_count: int = st.number_input(
            label=f"Number of Courses in {dept_name}:",
            min_value=1,
            max_value=20,
            value=3,
            key=f"course_count_{i}",
        )
        courses: list[Course] = []
        for j in range(course_count):
            course_name: str = st.text_input(
                label=f"Course {j + 1} Name in {dept_name}:", key=f"course_name_{i}_{j}"
            )
            course_lectures: int = st.number_input(
                label=f"Number of Lectures per Week for {course_name}:",
                min_value=1,
                max_value=10,
                value=3,
                key=f"course_lectures_{i}_{j}",
            )
            course_labs: int = st.number_input(
                label=f"Number of Labs per Week for {course_name}:",
                min_value=0,
                max_value=5,
                value=1,
                key=f"course_labs_{i}_{j}",
            )
            professor_options: list[str] = [prof.name for prof in data.professors]
            selected_professors: list[str] = st.multiselect(
                label=f"Professors for {course_name}:",
                options=professor_options,
                key=f"professors_{i}_{j}",
            )

            professors: list[Professor] = [
                prof for prof in data.professors if prof.name in selected_professors
            ]

            courses.append(
                Course(
                    number=f"C{j + 1}",
                    name=course_name,
                    professors=professors,
                    lectures_per_week=course_lectures,
                    labs_per_week=course_labs,
                )
            )
        data.add_dept(Department(name=dept_name, courses=courses))

    panel_count: int = st.number_input(
        label="Number of Panels:",
        min_value=1,
        max_value=15,
        value=2,
        key="panel_count",
    )

    for i in range(panel_count):
        panel_name: str = st.text_input(f"Panel {i + 1} Name:", key=f"panel_name_{i}")
        num_batches: int = st.number_input(
            label=f"Number of Batches in {panel_name}:",
            min_value=1,
            max_value=10,
            value=2,
            key=f"num_batches_{i}",
        )
        data.add_panel(Panel(name=panel_name, num_batches=num_batches))

    if st.button(label="Generate Timetable"):
        population: Population = Population(size=POPULATION_SIZE, data=data)
        genetic_algorithm: GeneticAlgorithm = GeneticAlgorithm()
        for generation in range(GENERATIONS):
            population = genetic_algorithm.evolve(population)
            best_schedule: Schedule = max(population.schedules, key=lambda s: s.fitness)
            if best_schedule.fitness == 1.0:
                break

        st.header(body="Generated Timetable")
        for panel in data.panels:
            st.subheader(f"Panel: {panel.name}")
            panel_schedules: list[Schedule] = [
                s for s in population.schedules if s.panel == panel
            ]
            if panel_schedules:
                best_panel_schedule: Schedule = max(
                    panel_schedules, key=lambda s: s.fitness
                )
                tabulate_schedule(schedule=best_panel_schedule)
            else:
                st.write(f"No schedule generated for panel {panel.name}.")


if __name__ == "__main__":
    main()
