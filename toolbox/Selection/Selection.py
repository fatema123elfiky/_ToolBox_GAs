from abc import ABC, abstractmethod
import random
from typing import Generic, TypeVar
from toolbox import *

class Selection(ABC):
    def __init__(self, fitness_function: FitnessFunction):
        self.fitness_function = fitness_function

    @abstractmethod
    def select(self, population: Population, num_parents: int) -> PairedPopulation:
        pass


class TournamentSelection(Selection):
    def __init__(self, fitness_function: FitnessFunction):
        super().__init__(fitness_function)

    def select(self, population: Population, num_parents: int) -> PairedPopulation:
        return []  # tournament implementation placeholder


class RouletteWheelSelection(Selection):
    def __init__(self, fitness_function: FitnessFunction):
        super().__init__(fitness_function)

    def select(self, population: Population, num_parents: int) -> PairedPopulation:
        return []  # roulette wheel implementation placeholder
