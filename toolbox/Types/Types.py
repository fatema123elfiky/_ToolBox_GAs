from toolbox import *
from collections.abc import Callable

Population = list[Chromosome]
ChromosomePair = tuple[Chromosome, Chromosome]
PairedPopulation = list[ChromosomePair]
FitnessFunction = Callable[[Chromosome], int]
