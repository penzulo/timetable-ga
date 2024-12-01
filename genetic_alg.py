from datetime import datetime, timedelta
from random import choice, randint, random, sample
from typing import Callable, List, Optional, Tuple

from constants import UNIVERSITY_END_TIME, UNIVERSITY_START_TIME
from models import ScheduledClass
from schedule import ScheduleOptimizer

# Type Aliases
SchedulePool = List[ScheduleOptimizer]
SchedFactory = Callable[[], ScheduleOptimizer]
NullableSchedulePool = Optional[SchedulePool]


class Population:
    def __init__(
        self,
        size: int,
        schedule_factory: SchedFactory,
        schedules: NullableSchedulePool = None,
    ) -> None:
        if not size > 0:
            raise ValueError("Expected a valid positive float for size.")

        self.size: int = size
        if schedules:
            self.schedules: SchedulePool = schedules
            return
        self.schedules: SchedulePool = [
            schedule_factory().create_schedule() for _ in range(size)
        ]

    def evaulaute_fitness(self) -> None:
        for schedule in self.schedules:
            schedule.fitness = schedule.calculate_fitness()

    def get_best_schedule(self) -> ScheduleOptimizer:
        return max(self.schedules, key=lambda s: s.fitness)

    def select_parents(self) -> Tuple[ScheduleOptimizer, ScheduleOptimizer]:
        parent1: ScheduleOptimizer = self._tournament_selection(self.schedules)
        parent2: ScheduleOptimizer = self._tournament_selection(self.schedules)
        return parent1, parent2

    def _roulette_selection(self, total_fitness: float) -> ScheduleOptimizer:
        pick: float = random() * total_fitness
        current: float = 0
        for schedule in self.schedules:
            current += (
                schedule.fitness
                if schedule.fitness != 0 or schedule.fitness != -1
                else schedule.calculate_fitness()
            )
            if current > pick:
                return schedule

        # In case of rounding errors, return the last one
        return self.schedules[-1]

    def _tournament_selection(self, population: SchedulePool) -> ScheduleOptimizer:
        tournament: SchedulePool = sample(population, len(population) * 5 // 100)
        return max(tournament, key=lambda s: s.fitness)


class EvolutionManager:
    """
    Handles the evolutionary process for optimizing schedules using genetic algorithms.

    Attributes:
        _mutation_rate (float): The probability of mutation occurring during evolution.
        _crossover_rate (float): The probability of crossover occurring during evolution.
    """

    def __init__(self, mutation_rate: float, crossover_rate: float) -> None:
        """
        Initializes the EvolutionManager with mutation and crossover rates.

        Args:
            mutation_rate (float): The probability of mutation (must be > 0.0).
            crossover_rate (float): The probability of crossover (must be > 0.0).

        Raises:
            ValueError: If either mutation_rate or crossover_rate is not a positive float.
        """
        if not isinstance(mutation_rate, float) or not mutation_rate > 0.0:
            raise ValueError(f"Expected a positive float mutation rate")

        if not isinstance(crossover_rate, float) or not mutation_rate > 0.0:
            raise ValueError(f"Expected a positive float crossover rate")

        self._mutation_rate: float = mutation_rate
        self._crossover_rate: float = crossover_rate

    def mutate(self, schedule_optimizer: ScheduleOptimizer) -> None:
        """
        Applies cascade mutation to a given schedule by modifying a random class's time slot.

        Args:
            schedule_optimizer (ScheduleOptimizer): The schedule to be mutated.

        Side Effects:
            Modifies the `time_slot` of a random class in the schedule if mutation occurs.
        """
        if random() < self._mutation_rate:
            random_class: ScheduledClass = choice(schedule_optimizer.raw_schedule)
            new_start_time: datetime = random_class.time_slot.start + timedelta(
                hours=randint(-1, 1)
            )

            if UNIVERSITY_START_TIME <= new_start_time <= UNIVERSITY_END_TIME:
                random_class.time_slot.start = new_start_time

    def crossover(
        self,
        parent_a: ScheduleOptimizer,
        parent_b: ScheduleOptimizer,
        schedule_factory: SchedFactory,
    ) -> ScheduleOptimizer:
        """
        Creates an offspring schedule by combining the schedules of two parent schedules.

        Args:
            parent_a (ScheduleOptimizer): The first parent schedule.
            parent_b (ScheduleOptimizer): The second parent schedule.
            schedule_factory (Callable[[], ScheduleOptimizer]): A factory function for creating a new ScheduleOptimizer instance.

        Returns:
            ScheduleOptimizer: The offspring schedule created from the two parents.
        """
        if random() > self._crossover_rate:
            # No crossover, return one parent
            return choice([parent_a, parent_b])

        offspring: ScheduleOptimizer = schedule_factory()

        offspring.raw_schedule = [
            choice([class_a, class_b])
            for class_a, class_b in zip(parent_a.raw_schedule, parent_b.raw_schedule)
        ]

        offspring.rooms = parent_a.rooms
        offspring.lab_rooms = parent_b.lab_rooms
        offspring.departments = parent_a.departments
        offspring.divisions = parent_b.divisions
        return offspring

    def evolve(
        self, population: Population, schedule_factory: SchedFactory
    ) -> Population:
        """
        Evolves a population to create the next generation of schedules.

        The evolution process involves selecting the best schedule, performing crossover
        and mutation, and forming a new population.

        Args:
            population (Population): The current population of schedules.
            schedule_factory (Callable[[], ScheduleOptimizer]): A factory function for creating a new ScheduleOptimizer instance.

        Returns:
            Population: The next generation of schedules.
        """
        next_generation: SchedulePool = [population.get_best_schedule()]

        while len(next_generation) < len(population.schedules):
            parent_a, parent_b = population.select_parents()
            offspring = self.crossover(parent_a, parent_b, schedule_factory)
            self.mutate(offspring)
            next_generation.append(offspring)

        new_population: Population = Population(
            size=len(next_generation),
            schedule_factory=schedule_factory,
            schedules=next_generation,
        )
        new_population.schedules = next_generation
        new_population.evaulaute_fitness()
        return new_population
