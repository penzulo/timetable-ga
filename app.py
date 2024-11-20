
from json import load
from typing import List
from datetime import datetime

from constants import CROSSOVER_RATE, GENERATIONS, MUTATION_RATE, POPULATION_SIZE
from data import sort_and_display
from genetic_alg import EvolutionManager, Population
from models import Course, Department, Division, Professor, Room
from schedule import ScheduleOptimizer


def do_time_slots_intersect(start1, end1, start2, end2):
    """
    Check if two time slots intersect, including edge cases where one ends as the other starts.

    Parameters:
        start1 (str): Start time of the first slot in %H:%M format.
        end1 (str): End time of the first slot in %H:%M format.
        start2 (str): Start time of the second slot in %H:%M format.
        end2 (str): End time of the second slot in %H:%M format.

    Returns:
        bool: True if the time slots intersect, False otherwise.
    """
    # Convert strings to datetime objects
    start1 = datetime.strptime(start1, "%H:%M")
    end1 = datetime.strptime(end1, "%H:%M")
    start2 = datetime.strptime(start2, "%H:%M")
    end2 = datetime.strptime(end2, "%H:%M")

    # Check for overlap
    return start1 < end2 and start2 < end1


def load_data() -> ScheduleOptimizer:
    with open("input.json", "r") as f:
        data = load(f)

    rooms = [Room(room["room_number"]) for room in data["rooms"]]
    lab_rooms = [Room(room["room_number"]) for room in data["lab_rooms"]]
    professors = [
        Professor(
            name=prof["name"],
            available_start=prof["available"]["start"],
            available_end=prof["available"]["end"],
        )
        for prof in data["professors"]
    ]

    departments: List[Department] = []
    for dept in data["departments"]:
        department = Department(dept["department_name"])
        department.offered_courses = [
            Course(
                title=course["title"],
                weekly_lectures=course["weekly_lectures"],
                weekly_labs=course["weekly_labs"],
            )
            for course in dept["offered_courses"]
        ]
        departments.append(department)

    prof_index = 0
    lab_prof_index = len(professors) // 2

    for dept in departments:
        for course in dept.offered_courses:
            course.assign_professor(professors[prof_index])
            prof_index = (prof_index + 1) % len(professors)

            if course.weekly_labs > 0:
                course.assign_lab_professor(professors[lab_prof_index])
                lab_prof_index = (lab_prof_index + 1) % len(professors)

    divisions: List[Division] = [
        Division(name=div["name"], num_batches=div["num_batches"])
        for div in data["divisions"]
    ]

    default_schedule = ScheduleOptimizer()
    for room in rooms:
        default_schedule.register_room(room)

    for lab_room in lab_rooms:
        default_schedule.register_lab_room(lab_room)

    for department in departments:
        default_schedule.register_department(department)

    for division in divisions:
        default_schedule.register_division(division)

    default_schedule.populate_time_slots()

    for dept in default_schedule.departments:
        for course in dept.offered_courses:
            availStart = course.assigned_professor.available_start
            availEnd = course.assigned_professor.available_end
            for tslot in default_schedule.time_slots:
                if not do_time_slots_intersect(
                    availStart, availEnd, tslot.start, tslot.end
                ):
                    course.assigned_professor.reserve_professor(tslot)
                    #course.lab_professor.reserve_professor(tslot)

    return default_schedule


def main() -> None:
    # data = load_data()
    # for dept in data.departments:
    #     for course in dept.offered_courses:
    #         availStart = course.assigned_professor.available_start
    #         availEnd = course.assigned_professor.available_end
    #         for tslot in data.time_slots:
    #             if not do_time_slots_intersect(
    #                 availStart, availEnd, tslot.start, tslot.end
    #             ):
    #                 print(f"intersecting: {tslot}")

    def schedule_factory():
        return load_data()

    initial_population = Population(
        size=POPULATION_SIZE, schedule_factory=schedule_factory
    )
    evolution_manager = EvolutionManager(
        mutation_rate=MUTATION_RATE, crossover_rate=CROSSOVER_RATE
    )

    current_population = initial_population
    for generation in range(1, GENERATIONS + 1):
        print(
            f"Generation {generation} - Best Fitness: {current_population.get_best_schedule().calculate_fitness()}"
        )
        current_population = evolution_manager.evolve(
            current_population, schedule_factory
        )

    best_schedule = current_population.get_best_schedule()
    print(f"Best Schedule Found!")
    sort_and_display(best_schedule)


if __name__ == "__main__":
    main()
