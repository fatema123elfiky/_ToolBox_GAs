from abc import ABC, abstractmethod

class FittnessFunction(ABC):
    @abstractmethod
    def evaluate(self, pop):
        pass

