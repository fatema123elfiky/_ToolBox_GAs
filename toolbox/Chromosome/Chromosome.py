from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import random
import copy

T = TypeVar('T')

class Chromosome(ABC, Generic[T]):
    def __init__(self, genes: list[T]):
        self.genes = list(genes)

    def GetRandomChromosome(self):
        new = copy.copy(self)
        new.genes = self.GenerateRandomChromosome()
        return new

    def clone(self):
        new = copy.copy(self)
        new.genes = copy.deepcopy(self.genes)
        return new

    def __len__(self) -> int:
        return len(self.genes)

    def __getitem__(self, index):
        return self.genes[index]

    def __setitem__(self, index, value):
        self.genes[index] = value

    def __eq__(self, other) -> bool:
        if isinstance(other, Chromosome):
            return self.genes == other.genes
        return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(genes={self.genes})"

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
        return len(genes) == self.size and all(gene in (0, 1) for gene in genes)


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
        return len(genes) == self.size and all(self.LowerBound <= gene <= self.UpperBound for gene in genes)


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
        return len(genes) == self.size and all(self.LowerBound <= gene <= self.UpperBound for gene in genes)


class PermutationChromosome(Chromosome[int]):
    def __init__(self, size: int, genes: list[int] | None = None, start_gene: int = 1):
        self.size = size
        self.start_gene = start_gene
        if genes is None:
            genes = self.GenerateRandomChromosome()
        super().__init__(genes)
        if not self.Validate(self.genes):
            raise ValueError(f"Invalid genes for PermutationChromosome. Genes must be a permutation of integers from {self.start_gene} to {self.start_gene + self.size - 1}.")

    def Validate(self, genes: list[int]) -> bool:
        expected = list(range(self.start_gene, self.start_gene + self.size))
        return sorted(genes) == expected

    def GenerateRandomChromosome(self) -> list[int]:
        genes = list(range(self.start_gene, self.start_gene + self.size))
        random.shuffle(genes)
        return genes
