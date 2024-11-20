from random import choice, random, sample
from typing import Callable, List

from models import ScheduledClass, TimeSlot
from schedule import ScheduleOptimizer


class Population:
    def __init__(
        self, size: int, schedule_factory: Callable[[], ScheduleOptimizer]
    ) -> None:
        if not size > 0:
            raise ValueError("Expected a valid positive float for size.")

        self.size: int = size
        self.schedules: List[ScheduleOptimizer] = [
            self._create_independant_schedule(schedule_factory) for _ in range(size)
        ]

    @staticmethod
    def _create_independant_schedule(
        schedule_factory: Callable[[], ScheduleOptimizer]
    ) -> ScheduleOptimizer:
        schedule = schedule_factory()
        schedule.populate_time_slots()
        schedule.create_schedule()
        return schedule

    def evaulaute_fitness(self) -> None:
        for schedule in self.schedules:
            schedule.fitness = schedule.calculate_fitness()

    def get_best_schedule(self) -> ScheduleOptimizer:
        return max(self.schedules, key=lambda s: s.fitness)

    def select_parents(self) -> List[ScheduleOptimizer]:
        total_fitness: float = sum(schedule.fitness for schedule in self.schedules)
        if total_fitness == 0:
            return sample(
                self.schedules, 2
            )  # If all fitnesses are 0, we will select randomly

        return [
            self._roulette_selection(total_fitness),
            self._roulette_selection(total_fitness),
        ]

    def _roulette_selection(self, total_fitness: float) -> ScheduleOptimizer:
        pick: float = random() * total_fitness
        current: float = 0
        for schedule in self.schedules:
            current += (
                schedule.fitness
                if schedule.fitness != 0
                else schedule.calculate_fitness()
            )
            if current > pick:
                return schedule

        # In case of rounding errors, return the last one
        return self.schedules[-1]


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
        Applies mutation to a given schedule by modifying a random class's time slot.

        Args:
            schedule_optimizer (ScheduleOptimizer): The schedule to be mutated.

        Side Effects:
            Modifies the `time_slot` of a random class in the schedule if mutation occurs.
        """
        if random() < self._mutation_rate:
            random_class: ScheduledClass = choice(schedule_optimizer.raw_schedule)
            random_time_slot: TimeSlot = choice(list(schedule_optimizer.time_slots))

            # if not schedule_optimizer.is_conflicting(
            #     random_time_slot, random_class.room, random_class.professor
            # ):
            random_class.time_slot = random_time_slot

    def crossover(
        self,
        parent_a: ScheduleOptimizer,
        parent_b: ScheduleOptimizer,
        schedule_factory: Callable[[], ScheduleOptimizer],
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

        offspring = schedule_factory()

        offspring.raw_schedule = [
            choice([class_a, class_b])
            for class_a, class_b in zip(parent_a.raw_schedule, parent_b.raw_schedule)
        ]

        offspring.rooms = parent_a.rooms.copy()
        offspring.lab_rooms = parent_a.lab_rooms.copy()
        offspring.time_slots = parent_a.time_slots.copy()
        offspring.departments = parent_a.departments.copy()
        offspring.divisions = parent_a.divisions.copy()
        offspring.fitness = offspring.calculate_fitness()
        return offspring

    def evolve(
        self, population: Population, schedule_factory: Callable[[], ScheduleOptimizer]
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
        next_generation: List[ScheduleOptimizer] = [population.get_best_schedule()]

        while len(next_generation) < len(population.schedules):
            parent_a, parent_b = population.select_parents()
            try:
                offspring = self.crossover(parent_a, parent_b, schedule_factory)
                self.mutate(offspring)
                next_generation.append(offspring)
            except (IndexError, ValueError):
                continue  # Skips this offspring if mutation or crossover fails

        new_population: Population = Population(
            size=len(next_generation), schedule_factory=schedule_factory
        )
        new_population.schedules = next_generation
        new_population.evaulaute_fitness()
        return new_population
