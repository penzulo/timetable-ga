import json

from constants import GENERATIONS, POPULATION_SIZE
from data import tabulate_schedule
from genetic_alg import GeneticAlgorithm, Population
from models import Course, Department, Panel, Professor, Room
from schedule import Data


def generate_sample_data():
    data = Data()

    # Add rooms
    for i in range(1, 6):
        data.add_room(Room(f"R10{i}"))
        data.add_lab_room(Room(f"L20{i}"))

    # Add professors
    # professor_names: list[str] = []
    with open("input.json", "r") as json_file:
        professor_names: list[str] = [
            professor["name"] for professor in json.load(json_file)["professors"]
        ]

    for i, name in enumerate(professor_names, 1):
        data.add_professor(Professor(f"P{i}", f"Dr. {name}"))

    # Add departments and courses
    departments = [
        (
            "Computer Science",
            ["Introduction to Programming", "Data Structures", "Algorithms"],
        )
    ]

    for dept_name, course_names in departments:
        courses = []
        for i, course_name in enumerate(course_names, 1):
            professors = [data.professors[j] for j in range(i - 1, i + 2)]
            course = Course(
                f"C{i}", course_name, professors, lectures_per_week=3, labs_per_week=1
            )
            courses.append(course)
        data.add_dept(Department(dept_name, courses))

    # Add panels
    data.add_panel(Panel("A", 2))

    # Generate class times
    data.generate_class_times()

    # Assign the slots which the professors are available for
    data.assign_professor_availability()

    return data


def test_genetic_algorithm(data):
    population = Population(POPULATION_SIZE, data)
    genetic_algorithm = GeneticAlgorithm()

    for generation in range(GENERATIONS):
        population = genetic_algorithm.evolve(population)
        best_schedule = max(population.schedules, key=lambda s: s.fitness)
        print(f"Generation {generation + 1}: Best Fitness = {best_schedule.fitness}")

        if best_schedule.fitness == 1.0:
            print("Perfect schedule found!")
            break

    # Print the best schedule for each panel
    for panel in data.panels:
        print(f"\nBest Schedule for Panel: {panel.name}")
        panel_schedules = [s for s in population.schedules if s._panel == panel]
        if panel_schedules:
            best_panel_schedule = max(panel_schedules, key=lambda s: s.fitness)
            tabulate_schedule(best_panel_schedule)
        else:
            print(f"No schedule generated for panel {panel.name}.")


if __name__ == "__main__":
    sample_data: Data = generate_sample_data()
    test_genetic_algorithm(sample_data)
