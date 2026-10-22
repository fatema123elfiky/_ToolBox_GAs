from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import random
import copy

T = TypeVar('T')

class Chromosome(ABC, Generic[T]):
    def __init__(self, genes: list[T]):
        self.genes = genes

    def GetRandomChromosome(self):
        new = copy.copy(self)
        new.genes = self.GenerateRandomChromosome()
        return new

    @abstractmethod
    def GenerateRandomChromosome(self) -> list[T]:
        pass

    @abstractmethod
    def Validate(self, genes: list[T]) -> bool:
        pass


class SimpleChromosome(Chromosome[T], ABC):
    def __init__(self, genes: list[T]):
        super().__init__(genes)
        
    @abstractmethod
    def GenerateRandomGene(self) -> T:
        pass

    def GenerateRandomChromosome(self) -> list[T]:
        return [self.GenerateRandomGene() for _ in range(self.size)]


class BinaryChromosome(SimpleChromosome[int]):
    def __init__(self, size: int, genes: list[int] | None = None):
        self.size = size
        if genes is None:
            genes = self.GenerateRandomChromosome()
        super().__init__(genes)
        if not self.Validate(self.genes):
            raise ValueError("Invalid genes for BinaryChromosome. Genes must be binary (0 or 1).")

    def GenerateRandomGene(self) -> int:
        return random.randint(0, 1)

    def Validate(self, genes: list[int]) -> bool:
        return all(gene in [0, 1] for gene in genes)


class IntegerChromosome(SimpleChromosome[int]):
    def __init__(self, size: int, LowerBound: int, UpperBound: int, genes: list[int] | None = None):
        self.size = size
        self.LowerBound = LowerBound
        self.UpperBound = UpperBound
        if genes is None:
            genes = self.GenerateRandomChromosome()
        super().__init__(genes)
        if not self.Validate(self.genes):
            raise ValueError("Invalid genes for IntegerChromosome. Genes must be within the given bounds.")

    def GenerateRandomGene(self) -> int:
        return random.randint(self.LowerBound, self.UpperBound)

    def Validate(self, genes: list[int]) -> bool:
        return all(self.LowerBound <= gene <= self.UpperBound for gene in genes)


class FloatChromosome(SimpleChromosome[float]):
    def __init__(self, size: int, LowerBound: float, UpperBound: float, AfterPoint: int, genes: list[float] | None = None):
        if AfterPoint < 0:
            raise ValueError("Invalid AfterPoint for FloatChromosome. AfterPoint must not be negative.")
        self.size = size
        self.LowerBound = LowerBound
        self.UpperBound = UpperBound
        self.AfterPoint = AfterPoint
        if genes is None:
            genes = self.GenerateRandomChromosome()
        else:
            genes = [round(gene, AfterPoint) for gene in genes]
        super().__init__(genes)
        if not self.Validate(self.genes):
            raise ValueError("Invalid genes for FloatChromosome. Genes must be within the given bounds.")

    def GenerateRandomGene(self) -> float:
        return round(random.uniform(self.LowerBound, self.UpperBound), self.AfterPoint)

    def Validate(self, genes: list[float]) -> bool:
        return all(self.LowerBound <= gene <= self.UpperBound for gene in genes)


class PermutationChromosome(Chromosome[int]):
    def __init__(self, size: int, genes: list[int] | None = None):
        self.size = size
        if genes is None:
            genes = self.GenerateRandomChromosome()
        super().__init__(genes)
        if not self.Validate(self.genes):
            raise ValueError("Invalid genes for PermutationChromosome. Genes must be a permutation of integers from 1 to size.")

    def Validate(self, genes: list[int]) -> bool:
        return sorted(genes) == list(range(1, self.size + 1))

    def GenerateRandomChromosome(self) -> list[int]:
        genes = list(range(1, self.size + 1))
        random.shuffle(genes)
        return genes
