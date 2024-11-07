from random import choice, random, randrange
from typing import Optional

from constants import (
    MUTATION_RATE,
    NUMB_OF_ELITE_SCHEDULES,
    POPULATION_SIZE,
    TOURNAMENT_SELECTION_SIZE,
)
from models import ClassTime, Professor, Room
from schedule import Data, Schedule


class Population:
    """
    Represents a population of schedules for a genetic algorithm.
    
    The `Population` class is responsible for initializing and managing a collection of `Schedule` objects, which represent potential solutions to a scheduling problem. The population is initialized with a specified size, and each schedule is created with a randomly assigned division from the provided `Data` object.
    
    The `schedules` property provides access to the list of schedules in the population.
    """
    def __init__(self, size: int, data: Data) -> None:
        self._schedules: list[Schedule] = []
        for _ in range(size):
            for division in data.divisions:
                self._schedules.append(Schedule(data=data, division=division).generate_schedule())

    @property
    def schedules(self) -> list[Schedule]:
        return self._schedules


class GeneticAlgorithm:
    """
    Implements the core functionality of the genetic algorithm for scheduling.
    
    The `GeneticAlgorithm` class provides static methods for performing the key operations of the genetic algorithm, including:
    
    - `_crossover_schedule`: Performs crossover between two schedules to create a new schedule.
    - `_mutate_schedule`: Mutates a given schedule by randomly changing the class times and rooms.
    - `_select_tournament_population`: Selects a tournament population from the overall population.
    - `_crossover_population`: Performs crossover on the population to create a new generation.
    - `_mutate_population`: Mutates the population to introduce diversity.
    - `evolve`: Evolves the population by performing crossover and mutation.
    
    These methods are used by the main `Population` class to manage the overall population of schedules and evolve them over generations to find an optimal solution.
    """
    @staticmethod
    def _crossover_schedule(schedule1: Schedule, schedule2: Schedule) -> Schedule:
        crossover_schedule: Schedule = Schedule(
            data=schedule1.data, division=schedule1.division
        ).generate_schedule()

        min_len: int = min(
            len(schedule1.classes),
            len(schedule2.classes),
            len(crossover_schedule.classes),
        )

        for i in range(min_len):
            if random() > 0.5:
                crossover_schedule.classes[i] = schedule1.classes[i]
            else:
                crossover_schedule.classes[i] = schedule2.classes[i]
        return crossover_schedule

    @staticmethod
    def _mutate_schedule(mutate_schedule: Schedule) -> None:
        try:
            for cls in mutate_schedule.classes:
                professor: Optional[Professor] = next(
                    (
                        prof
                        for prof in mutate_schedule.data.professors
                        if prof.name == cls.professor
                    ),
                    None,
                )

                if professor is None:
                    print(
                        f"[WARNING] No professor found with the name {cls.professor}. Skipping mutation for this class"
                    )
                    continue

                if random() < MUTATION_RATE:
                    class_duration: str = cls.class_time.split(" ")[2].strip("()")
                    available_times: list[ClassTime] = [
                        t
                        for t in professor.available_times
                        if t.duration == class_duration
                    ]
                    available_rooms: list[Room] = mutate_schedule.data.rooms.copy()

                    if available_times:
                        chosen: ClassTime = choice(available_times)
                        cls.class_time = (
                            f"{chosen.day} {chosen.time} ({chosen.duration})"
                        )
                    else:
                        print(
                            f"[WARNING] No available times matching duration for professor {professor.name}"
                            f"Skippping time mutation for this class."
                        )

                    if available_rooms:
                        cls.room = choice(available_rooms).number
                    else:
                        print(
                            f"No available rooms to mutate. Skipping room mutation for this class."
                        )
        except Exception as err:
            print(f"An error occurred during mutation: {err}")

    @staticmethod
    def _select_tournament_population(pop: Population) -> Population:
        tournament_pop: Population = Population(size=0, data=pop.schedules[0].data)
        for _ in range(TOURNAMENT_SELECTION_SIZE):
            tournament_pop.schedules.append(
                pop.schedules[randrange(start=0, stop=len(pop.schedules))]
            )
        tournament_pop.schedules.sort(key=lambda x: x.fitness, reverse=True)
        return tournament_pop

    def _crossover_population(self, pop: Population) -> Population:
        crossover_pop: Population = Population(size=0, data=pop.schedules[0].data)
        for i in range(NUMB_OF_ELITE_SCHEDULES):
            crossover_pop.schedules.append(pop.schedules[i])
        num: int = NUMB_OF_ELITE_SCHEDULES
        while num < POPULATION_SIZE:
            schedule1: Schedule = self._select_tournament_population(pop).schedules[0]
            schedule2: Schedule = self._select_tournament_population(pop).schedules[0]
            crossover_pop.schedules.append(
                self._crossover_schedule(schedule1, schedule2)
            )
            num += 1
        return crossover_pop

    def _mutate_population(self, population: Population) -> Population:
        for i in range(NUMB_OF_ELITE_SCHEDULES, POPULATION_SIZE):
            self._mutate_schedule(population.schedules[i])
        return population

    def evolve(self, population: Population) -> Population:
        return self._mutate_population(self._crossover_population(population))
