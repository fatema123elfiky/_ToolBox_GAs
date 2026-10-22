from abc import ABC, abstractmethod
from toolbox import *


class Replacement(ABC):
    def __init__(self, fitness_function: FitnessFunction):
        self.fitness_function = fitness_function

    @abstractmethod
    def replace(self, population: Population, offspring: Population) -> Population:
        pass


class FullReplacement(Replacement):
    def __init__(self, fitness_function: FitnessFunction):
        super().__init__(fitness_function)

    def replace(self, population: Population, offspring: Population) -> Population:
        return population  # full replacement implementation placeholder


class MixedReplacement(Replacement):
    def __init__(self, fitness_function: FitnessFunction):
        super().__init__(fitness_function)

    def replace(self, population: Population, offspring: Population) -> Population:
        return population  # mixed replacement implementation placeholder