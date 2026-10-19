from abc import ABC, abstractmethod
import random 


class MutationStrategy(ABC):
    @abstractmethod
    def mutate(self, chromosome, mp):
        pass

class FlipMuation(MutationStrategy):
    def mutate(self, chromosome, mp):
        for i in range(len(chromosome)):

            r = random.uniform(0,1)
            if r <= mp:
                if chromosome[i] == 0:
                    chromosome[i] = 1
                else:
                    chromosome[i] = 0

        return chromosome
