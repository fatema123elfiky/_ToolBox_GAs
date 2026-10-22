from typing import Generic, TypeVar
from toolbox import *

T = TypeVar('T', bound=Chromosome)

class GeneticAlgorithm(Generic[T]):
    def __init__(self,
                 fitness_function: FitnessFunction,
                 selection: Selection,
                 crossover: Crossover,
                 mutation: Mutation,
                 replacement: Replacement,
                 population_size: int,
                 TotalGenerations: int,
                 ChromosomePrototype: T,
                 population: Population | None = None,
                 ):
        self.fitness_function = fitness_function
        self.selection = selection
        self.crossover = crossover
        self.mutation = mutation
        self.replacement = replacement
        self.population_size = population_size
        self.TotalGenerations = TotalGenerations
        self.ChromosomePrototype = ChromosomePrototype
        if population is None:
            population = self.GeneratePopulation()
        self.population: list[T] = population
        self.current_generation = 0
        self.best_chromosome = self.GetBestChromosome()

    def GeneratePopulation(self) -> Population:
        return [self.ChromosomePrototype.GetRandomChromosome() for _ in range(self.population_size)]

    def GetBestChromosome(self) -> T | None:
        return max(self.population, key=self.fitness_function, default=None)

    def Run(self) -> T | None:
        for generation in range(self.TotalGenerations):
            self.current_generation = generation
            self.mutation.current_generation = generation
            self.mutation.TotalGenerations = self.TotalGenerations
            parents = self.selection.select(self.population, self.population_size)
            offspring_pairs = self.crossover.crossover(parents)
            mutated_offspring = [self.mutation.mutate(child)
                                 for pair in offspring_pairs
                                 for child in pair]
            self.population = self.replacement.replace(self.population, mutated_offspring)
            self.best_chromosome = self.GetBestChromosome()
        return self.best_chromosome
