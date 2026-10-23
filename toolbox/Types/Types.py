from __future__ import annotations
from typing import TYPE_CHECKING, Any
from collections.abc import Callable

if TYPE_CHECKING:
    from toolbox.Chromosome.Chromosome import Chromosome
else:
    from toolbox.Chromosome.Chromosome import Chromosome

Population = list[Chromosome]
ChromosomePair = tuple[Chromosome, Chromosome]
PairedPopulation = list[ChromosomePair]
FitnessFunction = Callable[[Any], float]
FeasibilityFunction = Callable[[Any], bool]
PenaltyFunction = Callable[[Any], float]
RepairFunction = Callable[[Any], Any]
