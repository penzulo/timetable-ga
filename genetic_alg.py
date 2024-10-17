from random import random, randrange

from constants import (
    NUMB_OF_ELITE_SCHEDULES,
    POPULATION_SIZE,
    TOURNAMENT_SELECTION_SIZE,
)
from schedule import Data, Schedule


class Population:
    def __init__(self, size: int, data: Data) -> None:
        self._schedules: list[Schedule] = []
        for _ in range(size):
            for panel in data.get_panels():
                self._schedules.append(Schedule(data=data, panel=panel).initialize())

    def get_schedules(self) -> list[Schedule]:
        return self._schedules


class GeneticAlgorithm:
    @staticmethod
    def _crossover_schedule(schedule1: Schedule, schedule2: Schedule) -> Schedule:
        crossover_schedule: Schedule = Schedule(
            data=schedule1.data, panel=schedule1.panel
        ).initialize()
        for i in range(len(crossover_schedule.get_classes())):
            if random() > 0.5:
                crossover_schedule.get_classes()[i] = schedule1.get_classes()[i]
            else:
                crossover_schedule.get_classes()[i] = schedule2.get_classes()[i]
        return crossover_schedule

    @staticmethod
    def _mutate_schedule(mutate_schedule: Schedule) -> None:
        schedule: Schedule = Schedule(
            data=mutate_schedule.data, panel=mutate_schedule.panel
        ).initialize()
        mutate_schedule._classes = schedule.get_classes()

    @staticmethod
    def _select_tournament_population(pop: Population) -> Population:
        tournament_pop: Population = Population(
            size=0, data=pop.get_schedules()[0].data
        )
        for _ in range(TOURNAMENT_SELECTION_SIZE):
            tournament_pop.get_schedules().append(
                pop.get_schedules()[randrange(start=0, stop=len(pop.get_schedules()))]
            )
        tournament_pop.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        return tournament_pop

    def _crossover_population(self, pop: Population) -> Population:
        crossover_pop: Population = Population(size=0, data=pop.get_schedules()[0].data)
        for i in range(NUMB_OF_ELITE_SCHEDULES):
            crossover_pop.get_schedules().append(pop.get_schedules()[i])
        num: int = NUMB_OF_ELITE_SCHEDULES
        while num < POPULATION_SIZE:
            schedule1: Schedule = self._select_tournament_population(
                pop
            ).get_schedules()[0]
            schedule2: Schedule = self._select_tournament_population(
                pop
            ).get_schedules()[0]
            crossover_pop.get_schedules().append(
                self._crossover_schedule(schedule1, schedule2)
            )
            num += 1
        return crossover_pop

    def _mutate_population(self, population: Population) -> Population:
        for i in range(NUMB_OF_ELITE_SCHEDULES, POPULATION_SIZE):
            self._mutate_schedule(population.get_schedules()[i])
        return population

    def evolve(self, population: Population) -> Population:
        return self._mutate_population(self._crossover_population(population))
