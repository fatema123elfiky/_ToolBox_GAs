from abc import ABC, abstractmethod
import random 

class Selection(ABC):
    @abstractmethod
    def select(self, pop, fitness, numofparents):
        pass

class RouletteWheel(Selection):
    def select(self, pop, fitness, numofparents):
        selected = []

        for _ in range(numofparents):
            R = random.uniform(0, sum(fitness))

            p = 0

            for i in range(len(pop)):
                p += fitness[i]

                if p >= R:
                    selected.append(pop[i])
                    break

        return selected
