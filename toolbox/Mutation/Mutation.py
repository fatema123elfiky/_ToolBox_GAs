from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import random
from toolbox.Chromosome.Chromosome import (
    Chromosome,
    SimpleChromosome,
    BinaryChromosome,
    FloatChromosome,
    PermutationChromosome,
)

T = TypeVar('T', bound=Chromosome)

class Mutation(Generic[T], ABC):
    def __init__(self, mutation_probability: float):
        self.mutation_probability = mutation_probability
        self.current_generation = 0
        self.TotalGenerations = 100

    @abstractmethod
    def mutate(self, chromosome: T) -> T:
        pass


class FlipMutation(Mutation[BinaryChromosome]):
    def __init__(self, mutation_probability: float):
        super().__init__(mutation_probability)

    def mutate(self, chromosome: BinaryChromosome) -> BinaryChromosome:
        for i in range(len(chromosome.genes)):
            r = random.uniform(0, 1)
            if r <= self.mutation_probability:
                chromosome.genes[i] ^= 1
        return chromosome


# Alias for backward compatibility
FlibMutation = FlipMutation


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
    def __init__(self, mutation_probability: float, Position1: int | None = None, Position2: int | None = None):
        self.Position1 = Position1
        self.Position2 = Position2
        super().__init__(mutation_probability)

    def mutate(self, chromosome: PermutationChromosome) -> PermutationChromosome:
        if random.uniform(0, 1) > self.mutation_probability or len(chromosome.genes) < 2:
            return chromosome

        if self.Position1 is not None and self.Position2 is not None:
            pos1, pos2 = self.Position1, self.Position2
            if not (0 <= pos1 < len(chromosome.genes)) or not (0 <= pos2 < len(chromosome.genes)):
                raise ValueError("Invalid positions for SwapMutation. Positions must be within the chromosome bounds.")
        else:
            pos1, pos2 = random.sample(range(len(chromosome.genes)), 2)

        chromosome.genes[pos1], chromosome.genes[pos2] = chromosome.genes[pos2], chromosome.genes[pos1]
        return chromosome


class InsertMutation(Mutation[PermutationChromosome]):
    def __init__(self, mutation_probability: float, Position1: int | None = None, Position2: int | None = None):
        self.Position1 = Position1
        self.Position2 = Position2
        super().__init__(mutation_probability)

    def mutate(self, chromosome: PermutationChromosome) -> PermutationChromosome:
        if random.uniform(0, 1) > self.mutation_probability or len(chromosome.genes) < 2:
            return chromosome

        if self.Position1 is not None and self.Position2 is not None:
            pos1, pos2 = self.Position1, self.Position2
            if not (0 <= pos1 < len(chromosome.genes)) or not (0 <= pos2 < len(chromosome.genes)):
                raise ValueError("Invalid positions for InsertMutation. Positions must be within the chromosome bounds.")
        else:
            pos1, pos2 = random.sample(range(len(chromosome.genes)), 2)

        gene = chromosome.genes.pop(pos1)
        chromosome.genes.insert(pos2, gene)
        return chromosome


class InversionMutation(Mutation[PermutationChromosome]):
    def __init__(self, mutation_probability: float, StartPoint: int | None = None, EndPoint: int | None = None):
        self.StartPoint = StartPoint
        self.EndPoint = EndPoint
        super().__init__(mutation_probability)

    def mutate(self, chromosome: PermutationChromosome) -> PermutationChromosome:
        if random.uniform(0, 1) > self.mutation_probability or len(chromosome.genes) < 2:
            return chromosome

        if self.StartPoint is not None and self.EndPoint is not None:
            start, end = self.StartPoint, self.EndPoint
            if not (0 <= start <= end <= len(chromosome.genes)):
                raise ValueError("Invalid range for InversionMutation. Range must be within the chromosome bounds.")
        else:
            pt1 = random.randint(0, len(chromosome.genes) - 2)
            pt2 = random.randint(pt1 + 1, len(chromosome.genes))
            start, end = pt1, pt2

        chromosome.genes[start:end] = chromosome.genes[start:end][::-1]
        return chromosome


class UniformMutation(Mutation[FloatChromosome]):
    def __init__(self, mutation_probability: float):
        super().__init__(mutation_probability)

    def mutate(self, chromosome: FloatChromosome) -> FloatChromosome:
        for i in range(len(chromosome.genes)):
            if random.uniform(0, 1) <= self.mutation_probability:
                chromosome.genes[i] = chromosome.GenerateRandomGene()
        return chromosome


class NonUniformMutation(Mutation[FloatChromosome]):
    def __init__(self, mutation_probability: float, B: float = 2.0, TotalGenerations: int = 100):
        self.B = B
        self.TotalGenerations = max(1, TotalGenerations)
        self.current_generation = 0
        super().__init__(mutation_probability)

    def mutate(self, chromosome: FloatChromosome) -> FloatChromosome:
        t = self.current_generation
        total_gen = max(1, self.TotalGenerations)
        tau = 1.0 - (t / total_gen)

        for i in range(len(chromosome.genes)):
            if random.uniform(0, 1) <= self.mutation_probability:
                x = chromosome.genes[i]
                r = random.uniform(0, 1)
                factor = 1.0 - (r ** (tau ** self.B))

                if random.random() < 0.5:
                    delta = (chromosome.UpperBound - x) * factor
                    new_val = x + delta
                else:
                    delta = (x - chromosome.LowerBound) * factor
                    new_val = x - delta

                new_val = max(chromosome.LowerBound, min(chromosome.UpperBound, new_val))
                chromosome.genes[i] = round(new_val, chromosome.AfterPoint)
        return chromosome