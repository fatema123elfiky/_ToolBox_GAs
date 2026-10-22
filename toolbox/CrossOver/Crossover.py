from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from toolbox import *

T = TypeVar('T', bound=Chromosome)

class Crossover(Generic[T], ABC):
    def __init__(self, crossover_probability, size):
        self.crossover_probability = crossover_probability
        self.size = size

    @abstractmethod
    def crossover(self, Parents: list[tuple[T, T]]) -> list[tuple[T, T]]:
        pass



class SinglePointCrossover(Crossover[SimpleChromosome]):
    def __init__(self, crossover_probability: float, size: int, Location: int):
        self.Location = Location
        self.size = size
        self.crossover_probability = crossover_probability
        if not self.Validate(Location):
            raise ValueError("Invalid crossover location for SinglePointCrossover.")
        super().__init__(self.crossover_probability, self.size)
        pass

    def Validate(self, Location: int) -> bool:
        if Location < 0 or Location >= self.size:
            return False
        return True

    def crossover(self, Parents: list[tuple[SimpleChromosome , SimpleChromosome]]) -> list[tuple[SimpleChromosome , SimpleChromosome]]:
        return Parents  # single-point implementation placeholder



class MultiPointCrossover(Crossover[SimpleChromosome]):
    def __init__(self, crossover_probability: float, size: int, NumberOfPoints: int, Locations: list[int]):
        self.crossover_probability = crossover_probability
        self.size = size
        self.NumberOfPoints = NumberOfPoints
        self.Locations = sorted(Locations)
        if not self.Validate(NumberOfPoints, self.Locations):
            raise ValueError("Invalid number of points or locations for MultiPointCrossover.")
        super().__init__(self.crossover_probability, self.size)
        pass

    def Validate(self, NumberOfPoints: int, Locations: list[int]) -> bool:
        if NumberOfPoints <= 0:
            return False
        if len(Locations) != NumberOfPoints:
            return False
        if any(loc < 0 or loc >= self.size for loc in Locations):
            return False
        return True

    def crossover(self, Parents: list[tuple[SimpleChromosome , SimpleChromosome]]) -> list[tuple[SimpleChromosome , SimpleChromosome]]:
        return Parents  # multi-point implementation placeholder


class UniformCrossover(Crossover[SimpleChromosome]):
    def __init__(self, crossover_probability: float, size: int, mask: list[bool]):
        self.crossover_probability = crossover_probability
        self.size = size
        self.mask = mask
        if not self.Validate(mask):
            raise ValueError("Invalid mask for UniformCrossover.")
        super().__init__(self.crossover_probability, self.size)
        pass

    def Validate(self, mask: list[bool]) -> bool:
        if len(mask) != self.size:
            return False
        return True

    def crossover(self, Parents: list[tuple[SimpleChromosome , SimpleChromosome]]) -> list[tuple[SimpleChromosome , SimpleChromosome]]:
        return Parents  # uniform implementation placeholder



class OrderCrossover(Crossover[PermutationChromosome]):
    def __init__(self, crossover_probability: float, size: int, StartPoint: int, EndPoint: int):
        self.crossover_probability = crossover_probability
        self.size = size
        self.StartPoint = StartPoint
        self.EndPoint = EndPoint    
        if not self.Validate(StartPoint, EndPoint):
            raise ValueError("Invalid start or end point for OrderCrossover.")
        super().__init__(self.crossover_probability, self.size)

    def Validate(self, StartPoint: int, EndPoint: int) -> bool:
        if StartPoint < 0 or StartPoint >= self.size:
            return False
        if EndPoint < 0 or EndPoint >= self.size:
            return False
        if StartPoint >= EndPoint:
            return False
        return True

    def crossover(self, Parents: list[tuple[PermutationChromosome , PermutationChromosome]]) -> list[tuple[PermutationChromosome , PermutationChromosome]]:
        return Parents  # order crossover implementation placeholder