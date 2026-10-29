from abc import ABC, abstractmethod
import random
from toolbox.Chromosome.Chromosome import Chromosome
from toolbox.Types.Types import Population, PairedPopulation, FitnessFunction

class Selection(ABC):
    def __init__(self, fitness_function: FitnessFunction | None = None, maximize: bool = True):
        self.fitness_function = fitness_function
        self.maximize = maximize

    @abstractmethod
    def select(self, population: Population, num_parents: int) -> PairedPopulation:
        pass


class TournamentSelection(Selection):
    def __init__(self, fitness_function: FitnessFunction | None = None, tournament_size: int = 3, maximize: bool = True):
        super().__init__(fitness_function, maximize)
        self.tournament_size = tournament_size

    def select(self, population: Population, num_parents: int) -> PairedPopulation:
        if not population:
            return []
        if self.fitness_function is None:
            raise ValueError("Fitness function must be provided to TournamentSelection.")

        selected: list[Chromosome] = []
        k = min(self.tournament_size, len(population))

        for _ in range(num_parents):
            competitors = random.sample(population, k)
            if self.maximize:
                winner = max(competitors, key=self.fitness_function)
            else:
                winner = min(competitors, key=self.fitness_function)
            selected.append(winner.clone())

        paired: PairedPopulation = []
        for i in range(0, len(selected) - 1, 2):
            paired.append((selected[i], selected[i + 1]))
        if len(selected) % 2 != 0:
            paired.append((selected[-1], selected[0].clone()))
        return paired


class RouletteWheelSelection(Selection):
    def __init__(self, fitness_function: FitnessFunction | None = None, maximize: bool = True):
        super().__init__(fitness_function, maximize)

    def select(self, population: Population, num_parents: int) -> PairedPopulation:
        if not population:
            return []
        if self.fitness_function is None:
            raise ValueError("Fitness function must be provided to RouletteWheelSelection.")

        fitness_values = [float(self.fitness_function(c)) for c in population]

        if not self.maximize:
            max_f = max(fitness_values)
            adj = [max_f - f + 1e-6 for f in fitness_values]
        else:
            min_f = min(fitness_values)
            if min_f <= 0:
                adj = [f - min_f + 1e-6 for f in fitness_values]
            else:
                adj = [f for f in fitness_values]

        total_fitness = sum(adj)
        if total_fitness <= 0:
            adj = [1.0] * len(population)
            total_fitness = float(len(population))

        selected: list[Chromosome] = []
        for _ in range(num_parents):
            r = random.uniform(0, total_fitness)
            cumulative = 0.0
            chosen = population[-1]
            for chrom, fit in zip(population, adj):
                cumulative += fit
                if cumulative >= r:
                    chosen = chrom
                    break
            selected.append(chosen.clone())

        paired: PairedPopulation = []
        for i in range(0, len(selected) - 1, 2):
            paired.append((selected[i], selected[i + 1]))
        if len(selected) % 2 != 0:
            paired.append((selected[-1], selected[0].clone()))
        return paired
