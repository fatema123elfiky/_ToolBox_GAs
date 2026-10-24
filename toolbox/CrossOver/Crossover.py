from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from toolbox import *
import copy
import random


T = TypeVar('T', bound=Chromosome)

class Crossover(Generic[T], ABC):
    def __init__(self, crossover_probability, size):
        self.crossover_probability = crossover_probability
        self.size = size
    def check_crossOver_probability(self) -> bool:
        r1 = round(random.uniform(1.5, 9.5), 2)
        if r1 <= self.crossover_probability:
            return True
        return False    


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
    def __init__(self, crossover_probability: float, size: int, NumberOfPoints: int ):#  Locations: list[int]
        self.crossover_probability = crossover_probability
        self.size = size 
        self.NumberOfPoints = NumberOfPoints
        self.Locations: list[int] = []
        #self.Locations # = sorted(Locations)# would not be used only generated
        if not self.Validate(NumberOfPoints, self.Locations):
            raise ValueError("Invalid number of points or locations for MultiPointCrossover.")
        super().__init__(self.crossover_probability, self.size)
        pass

    def Validate(self, NumberOfPoints: int, Locations: list[int]) -> bool:
        if NumberOfPoints <= 0  or NumberOfPoints >= self.size:
            return False
        #if len(Locations) != NumberOfPoints:
         #   return False
        #if any(loc < 0 or loc >= self.size for loc in Locations):
         #   return False
        return True

    def crossover(self, Parents: list[tuple[SimpleChromosome , SimpleChromosome]]) -> list[tuple[SimpleChromosome , SimpleChromosome]]:
        returned_offspring : list[tuple[SimpleChromosome , SimpleChromosome]] = []
        for chromosome_one , chromosome_two in Parents :
            if super().check_crossOver_probability() :
                self.Locations = random.sample(range(0,self.size-1), self.NumberOfPoints)   
                self.Locations.sort()
                genes_one ,genes_two = [] ,[]
                shuffle : bool = False
                idx_r2 = 0
                for idx in range(0,self.size):
                      if shuffle :
                        genes_two.append(chromosome_one.genes[idx])
                        genes_one.append(chromosome_two.genes[idx])
                      else :
                        genes_two.append(chromosome_two.genes[idx])
                        genes_one.append(chromosome_one.genes[idx])

                      if  idx_r2 < len(self.Locations) and idx == self.Locations[idx_r2]:
                        idx_r2+=1
                        shuffle = not shuffle   

                child_one = copy.deepcopy(chromosome_one)
                child_two = copy.deepcopy(chromosome_two)
                child_one.genes = genes_one
                child_two.genes = genes_two        

                returned_offspring.append((child_one,child_two))

            else:
                returned_offspring.append((chromosome_one,chromosome_two))   

        return  returned_offspring        



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