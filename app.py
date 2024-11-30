from collections import defaultdict
from random import randint
from timeit import default_timer as timer
from typing import DefaultDict

from constants import (
    CROSSOVER_RATE,
    GENERATIONS,
    MUTATION_RATE,
    POPULATION_SIZE,
    STAGNANCY_THRESHOLD,
)
from data import load_data, sort_and_display
from genetic_alg import EvolutionManager, Population
from schedule import ScheduleOptimizer


def schedule_factory() -> ScheduleOptimizer:
    return load_data()


def main() -> None:
    initial_population: Population = Population(
        size=POPULATION_SIZE, schedule_factory=schedule_factory
    )
    print("Initialized population successfully")
    evolution_manager: EvolutionManager = EvolutionManager(
        mutation_rate=MUTATION_RATE, crossover_rate=CROSSOVER_RATE
    )

    initial_population.evaulaute_fitness()
    current_population: Population = initial_population

    fitness_counts: DefaultDict[float, int] = defaultdict(int)

    for gen in range(GENERATIONS):
        start: float = timer()

        if gen % 15 == 0:
            current_population.schedules.extend(
                [schedule_factory().create_schedule() for _ in range(randint(10, 21))]
            )
        best_fitness: float = current_population.get_best_schedule().fitness
        fitness_counts[best_fitness] += 1
        if fitness_counts[best_fitness] > STAGNANCY_THRESHOLD:
            print("Stagnancy Threshold exceeded. Stopping evolution")
            break

        print(
            f"Generation {gen} -",
            f"Best Fitness: {best_fitness * 100:.3f} -",
            f" Took {timer() - start:.6f} seconds",
            sep=" "
        )

        current_population = evolution_manager.evolve(
            current_population, schedule_factory
        )

    best_schedule: ScheduleOptimizer = current_population.get_best_schedule()

    print(
        "Best Schedule Found!",
        f"Fitness: {best_schedule.fitness * 100:.3f}%",
        sort_and_display(best_schedule),
        sep="\n",
    )


if __name__ == "__main__":
    main()
