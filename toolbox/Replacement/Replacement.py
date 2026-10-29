from abc import ABC, abstractmethod
import random
from toolbox.Types.Types import Population, FitnessFunction

class Replacement(ABC):
    def __init__(self, fitness_function: FitnessFunction | None = None, maximize: bool = True):
        self.fitness_function = fitness_function
        self.maximize = maximize

    @abstractmethod
    def replace(self, population: Population, offspring: Population) -> Population:
        pass


class FullReplacement(Replacement):
    def __init__(self, fitness_function: FitnessFunction | None = None, elitism: int = 0, maximize: bool = True):
        super().__init__(fitness_function, maximize)
        self.elitism = elitism

    def replace(self, population: Population, offspring: Population) -> Population:
        target_size = len(population)
        if self.elitism > 0 and population:
            if self.fitness_function is None:
                raise ValueError("Fitness function must be provided to FullReplacement when elitism > 0.")
            elites = sorted(population, key=self.fitness_function, reverse=self.maximize)[:self.elitism]
            elites = [c.clone() for c in elites]
            remaining_slots = max(0, target_size - len(elites))
            sorted_offspring = sorted(offspring, key=self.fitness_function, reverse=self.maximize)
            new_pop = elites + [c.clone() for c in sorted_offspring[:remaining_slots]]
            # Fill with clones from offspring or population if fewer than target_size
            while len(new_pop) < target_size and (offspring or population):
                source = offspring if offspring else population
                new_pop.append(random.choice(source).clone())
            return new_pop
        new_pop = [c.clone() for c in offspring[:target_size]]
        while len(new_pop) < target_size and (offspring or population):
            source = offspring if offspring else population
            new_pop.append(random.choice(source).clone())
        return new_pop


class MixedReplacement(Replacement):
    def __init__(self, fitness_function: FitnessFunction | None = None, strong: int | None = None, maximize: bool = True):
        super().__init__(fitness_function, maximize)
        self.strong = strong

    def replace(self, population: Population, offspring: Population) -> Population:
        if self.fitness_function is None:
            raise ValueError("Fitness function must be provided to MixedReplacement.")
        target_size = len(population)
        strong_count = self.strong if self.strong is not None else max(1, target_size // 2)
        strong_count = min(strong_count, target_size)
        weak_count = target_size - strong_count

        combined = population + offspring
        combined.sort(key=self.fitness_function, reverse=self.maximize)

        new_pop = [c.clone() for c in combined[:strong_count]]
        remains = combined[strong_count:]
        if weak_count > 0:
            if len(remains) >= weak_count:
                rand_weak = random.sample(remains, weak_count)
            else:
                rand_weak = random.choices(remains, k=weak_count)
            new_pop.extend([c.clone() for c in rand_weak])
        return new_pop