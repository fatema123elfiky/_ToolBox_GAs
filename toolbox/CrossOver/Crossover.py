from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import copy
import random
from toolbox.Chromosome.Chromosome import (
    Chromosome,
    SimpleChromosome,
    PermutationChromosome,
)

T = TypeVar('T', bound=Chromosome)

class Crossover(Generic[T], ABC):
    def __init__(self, crossover_probability: float = 0.8, size: int = 10):
        self.crossover_probability = crossover_probability
        self.size = size

    def check_crossOver_probability(self) -> bool:
        return random.random() <= self.crossover_probability

    @abstractmethod
    def crossover(self, Parents: list[tuple[T, T]]) -> list[tuple[T, T]]:
        pass


class SinglePointCrossover(Crossover[SimpleChromosome]):
    def __init__(self, crossover_probability: float = 0.8, size: int = 10, Location: int | None = None):
        super().__init__(crossover_probability, size)
        self.Location = Location
        if Location is not None and not self.Validate(Location):
            raise ValueError("Invalid crossover location for SinglePointCrossover.")

    def Validate(self, Location: int) -> bool:
        return 0 <= Location < self.size

    def crossover(self, Parents: list[tuple[SimpleChromosome, SimpleChromosome]]) -> list[tuple[SimpleChromosome, SimpleChromosome]]:
        returned_offspring: list[tuple[SimpleChromosome, SimpleChromosome]] = []
        for p1, p2 in Parents:
            if self.check_crossOver_probability():
                cur_size = min(len(p1.genes), len(p2.genes))
                if cur_size > 1:
                    loc = self.Location if self.Location is not None else random.randint(1, cur_size - 1)
                    c1 = p1.clone()
                    c2 = p2.clone()
                    c1.genes = p1.genes[:loc] + p2.genes[loc:]
                    c2.genes = p2.genes[:loc] + p1.genes[loc:]
                    returned_offspring.append((c1, c2))
                else:
                    returned_offspring.append((p1.clone(), p2.clone()))
            else:
                returned_offspring.append((p1.clone(), p2.clone()))
        return returned_offspring


class MultiPointCrossover(Crossover[SimpleChromosome]):
    def __init__(self, crossover_probability: float = 0.8, size: int = 10, NumberOfPoints: int = 2):
        super().__init__(crossover_probability, size)
        self.NumberOfPoints = NumberOfPoints
        self.Locations: list[int] = []
        if not self.Validate(NumberOfPoints, self.Locations):
            raise ValueError("Invalid number of points for MultiPointCrossover.")

    def Validate(self, NumberOfPoints: int, Locations: list[int]) -> bool:
        return 0 < NumberOfPoints < max(2, self.size)

    def crossover(self, Parents: list[tuple[SimpleChromosome, SimpleChromosome]]) -> list[tuple[SimpleChromosome, SimpleChromosome]]:
        returned_offspring: list[tuple[SimpleChromosome, SimpleChromosome]] = []
        for chromosome_one, chromosome_two in Parents:
            if self.check_crossOver_probability() and self.size > 2:
                num_pts = min(self.NumberOfPoints, self.size - 1)
                self.Locations = sorted(random.sample(range(0, self.size - 1), num_pts))
                genes_one, genes_two = [], []
                shuffle: bool = False
                idx_r2 = 0
                for idx in range(self.size):
                    if shuffle:
                        genes_two.append(chromosome_one.genes[idx])
                        genes_one.append(chromosome_two.genes[idx])
                    else:
                        genes_two.append(chromosome_two.genes[idx])
                        genes_one.append(chromosome_one.genes[idx])

                    if idx_r2 < len(self.Locations) and idx == self.Locations[idx_r2]:
                        idx_r2 += 1
                        shuffle = not shuffle

                child_one = chromosome_one.clone()
                child_two = chromosome_two.clone()
                child_one.genes = genes_one
                child_two.genes = genes_two
                returned_offspring.append((child_one, child_two))
            else:
                returned_offspring.append((chromosome_one.clone(), chromosome_two.clone()))

        return returned_offspring


class UniformCrossover(Crossover[SimpleChromosome]):
    def __init__(self, crossover_probability: float = 0.8, size: int = 10, mask: list[bool] | None = None):
        super().__init__(crossover_probability, size)
        self.mask = mask
        if mask is not None and not self.Validate(mask):
            raise ValueError("Invalid mask for UniformCrossover.")

    def Validate(self, mask: list[bool]) -> bool:
        return len(mask) == self.size

    def crossover(self, Parents: list[tuple[SimpleChromosome, SimpleChromosome]]) -> list[tuple[SimpleChromosome, SimpleChromosome]]:
        returned_offspring: list[tuple[SimpleChromosome, SimpleChromosome]] = []
        for p1, p2 in Parents:
            if self.check_crossOver_probability():
                cur_size = min(len(p1.genes), len(p2.genes))
                cur_mask = self.mask if self.mask is not None else [random.random() < 0.5 for _ in range(cur_size)]
                c1 = p1.clone()
                c2 = p2.clone()
                g1 = list(p1.genes)
                g2 = list(p2.genes)
                for i in range(min(cur_size, len(cur_mask))):
                    if not cur_mask[i]:
                        g1[i], g2[i] = g2[i], g1[i]
                c1.genes = g1
                c2.genes = g2
                returned_offspring.append((c1, c2))
            else:
                returned_offspring.append((p1.clone(), p2.clone()))
        return returned_offspring


class OrderCrossover(Crossover[PermutationChromosome]):
    def __init__(
        self,
        crossover_probability: float = 0.8,
        size: int = 10,
        StartPoint: int | None = None,
        EndPoint: int | None = None,
    ):
        super().__init__(crossover_probability, size)
        self.StartPoint = StartPoint
        self.EndPoint = EndPoint
        if StartPoint is not None and EndPoint is not None and not self.Validate(StartPoint, EndPoint):
            raise ValueError("Invalid start or end point for OrderCrossover.")

    def Validate(self, StartPoint: int, EndPoint: int) -> bool:
        if StartPoint < 0 or StartPoint >= self.size:
            return False
        if EndPoint < 0 or EndPoint >= self.size:
            return False
        if StartPoint >= EndPoint:
            return False
        return True

    def _ox1_pair(self, p1: PermutationChromosome, p2: PermutationChromosome) -> tuple[PermutationChromosome, PermutationChromosome]:
        n = len(p1.genes)
        if n < 2:
            return p1.clone(), p2.clone()

        if self.StartPoint is not None and self.EndPoint is not None:
            start, end = self.StartPoint, self.EndPoint
        else:
            pt1 = random.randint(0, n - 2)
            pt2 = random.randint(pt1 + 1, n - 1)
            start, end = pt1, pt2

        def breed(parent1: PermutationChromosome, parent2: PermutationChromosome) -> PermutationChromosome:
            child_genes: list[int | None] = [None] * n
            child_genes[start:end + 1] = parent1.genes[start:end + 1]
            copied_set = set(child_genes[start:end + 1])

            p2_genes = parent2.genes
            cur_p2 = (end + 1) % n
            cur_child = (end + 1) % n

            for _ in range(n):
                gene = p2_genes[cur_p2]
                if gene not in copied_set:
                    child_genes[cur_child] = gene
                    cur_child = (cur_child + 1) % n
                cur_p2 = (cur_p2 + 1) % n

            child = parent1.clone()
            child.genes = [g for g in child_genes if g is not None]
            return child

        return breed(p1, p2), breed(p2, p1)

    def crossover(self, Parents: list[tuple[PermutationChromosome, PermutationChromosome]]) -> list[tuple[PermutationChromosome, PermutationChromosome]]:
        returned_offspring: list[tuple[PermutationChromosome, PermutationChromosome]] = []
        for p1, p2 in Parents:
            if self.check_crossOver_probability():
                c1, c2 = self._ox1_pair(p1, p2)
                returned_offspring.append((c1, c2))
            else:
                returned_offspring.append((p1.clone(), p2.clone()))
        return returned_offspring