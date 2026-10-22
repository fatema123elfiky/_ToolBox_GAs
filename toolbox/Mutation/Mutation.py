from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from toolbox import *
import random
T = TypeVar('T')

class Mutation(Generic[T], ABC):
    def __init__(self, mutation_probability: float):
        self.mutation_probability = mutation_probability

    @abstractmethod
    def mutate(self, chromosome: T) -> T:
        pass



class FlibMutation(Mutation[BinaryChromosome]):
    def __init__(self, mutation_probability: float):
        super().__init__(mutation_probability)

    def mutate(self, chromosome: BinaryChromosome) -> BinaryChromosome:
        for i in range(len(chromosome.genes)):
            r = random.uniform(0, 1)
            if r <= self.mutation_probability:
                chromosome.genes[i] ^= 1
        return chromosome



class RandomMutation(Mutation[SimpleChromosome]):
    def __init__(self, mutation_probability: float):
        super().__init__(mutation_probability)

    def mutate(self, chromosome: SimpleChromosome) -> SimpleChromosome:
        for i in range(len(chromosome.genes)):
            r = random.uniform(0, 1)
            if r <= self.mutation_probability:
                chromosome.genes[i] = chromosome.GenerateRandomGene()
        return chromosome



class SwapMutation(Mutation[PermutationChromosome]):
        def __init__(self, mutation_probability: float, Position1: int, Position2: int):
            self.Position1 = Position1
            self.Position2 = Position2
            super().__init__(mutation_probability)

        def mutate(self, chromosome: PermutationChromosome) -> PermutationChromosome:
            if not (0 <= self.Position1 < len(chromosome.genes)) or not (0 <= self.Position2 < len(chromosome.genes)):
                raise ValueError("Invalid positions for SwapMutation. Positions must be within the chromosome bounds.")
            if random.uniform(0, 1) > self.mutation_probability:
                return chromosome
            chromosome.genes[self.Position1], chromosome.genes[self.Position2] = \
                chromosome.genes[self.Position2], chromosome.genes[self.Position1]
            return chromosome

class InsertMutation(Mutation[PermutationChromosome]):
        def __init__(self, mutation_probability: float, Position1: int, Position2: int):
            self.Position1 = Position1
            self.Position2 = Position2
            super().__init__(mutation_probability)

        def mutate(self, chromosome: PermutationChromosome) -> PermutationChromosome:
            if not (0 <= self.Position1 < len(chromosome.genes)) or not (0 <= self.Position2 < len(chromosome.genes)):
                raise ValueError("Invalid positions for InsertMutation. Positions must be within the chromosome bounds.")
            if random.uniform(0, 1) > self.mutation_probability:
                return chromosome
            gene = chromosome.genes.pop(self.Position1)
            chromosome.genes.insert(self.Position2, gene)
            return chromosome

class InversionMutation(Mutation[PermutationChromosome]):
        def __init__(self, mutation_probability: float, StartPoint: int, EndPoint: int):
            self.StartPoint = StartPoint
            self.EndPoint = EndPoint
            super().__init__(mutation_probability)

        def mutate(self, chromosome: PermutationChromosome) -> PermutationChromosome:
            if not (0 <= self.StartPoint <= self.EndPoint <= len(chromosome.genes)):
                raise ValueError("Invalid range for InversionMutation. Range must be within the chromosome bounds.")
            if random.uniform(0, 1) > self.mutation_probability:
                return chromosome
            chromosome.genes[self.StartPoint:self.EndPoint] = chromosome.genes[self.StartPoint:self.EndPoint][::-1]
            return chromosome



class UniformMutation(Mutation[FloatChromosome]):
    def __init__(self, mutation_probability: float):
        super().__init__(mutation_probability)

    def mutate(self, chromosome: FloatChromosome) -> FloatChromosome:
        return chromosome  # uniform mutation implementation placeholder



class NonUniformMutation(Mutation[FloatChromosome]):
    def __init__(self, mutation_probability: float, B: float, TotalGenerations: int):
        self.B = B
        self.TotalGenerations = TotalGenerations
        self.current_generation = 0
        super().__init__(mutation_probability)

    def mutate(self, chromosome: FloatChromosome) -> FloatChromosome:
        return chromosome  # non-uniform placeholder — sees self.current_generation & self.TotalGenerations (updated by GA each generation)