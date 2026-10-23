from typing import Generic, TypeVar, Any
from collections.abc import Callable
import copy

from toolbox.Chromosome.Chromosome import (
    Chromosome,
    BinaryChromosome,
    IntegerChromosome,
    FloatChromosome,
    PermutationChromosome,
    SimpleChromosome,
)
from toolbox.Types.Types import (
    Population,
    FitnessFunction,
    FeasibilityFunction,
    PenaltyFunction,
    RepairFunction,
)
from toolbox.Selection.Selection import Selection, TournamentSelection
from toolbox.CrossOver.Crossover import (
    Crossover,
    SinglePointCrossover,
    OrderCrossover,
)
from toolbox.Mutation.Mutation import (
    Mutation,
    FlipMutation,
    RandomMutation,
    SwapMutation,
    NonUniformMutation,
)
from toolbox.Replacement.Replacement import Replacement, MixedReplacement

T = TypeVar('T', bound=Chromosome)


class GeneticAlgorithm(Generic[T]):
    """
    Modular Genetic Algorithm (GA) Engine.

    Features:
    - Default hyperparameters for all GA settings, with full user configurability.
    - User-provided fitness evaluation and feasibility check functions.
    - Flexible constraint handling for infeasible solutions (penalty method, death penalty,
      repair, rejection, or Deb's constraint rules).
    - Automatic default operator configuration based on chromosome prototype.
    """

    # Sensible default values for GA hyperparameters
    DEFAULT_POPULATION_SIZE: int = 50
    DEFAULT_TOTAL_GENERATIONS: int = 100
    DEFAULT_CROSSOVER_PROBABILITY: float = 0.8
    DEFAULT_MUTATION_PROBABILITY: float = 0.1
    DEFAULT_INFEASIBLE_HANDLING: str = "penalty"
    DEFAULT_PENALTY_VALUE: float = 1e6

    def __init__(
        self,
        fitness_function: FitnessFunction | None = None,
        ChromosomePrototype: T | None = None,
        chromosome_prototype: T | None = None,
        selection: Selection | None = None,
        crossover: Crossover | None = None,
        mutation: Mutation | None = None,
        replacement: Replacement | None = None,
        population_size: int = DEFAULT_POPULATION_SIZE,
        TotalGenerations: int | None = None,
        total_generations: int | None = None,
        crossover_probability: float | None = None,
        crossover_prob: float | None = None,
        mutation_probability: float | None = None,
        mutation_prob: float | None = None,
        feasibility_function: FeasibilityFunction | None = None,
        penalty_function: PenaltyFunction | None = None,
        repair_function: RepairFunction | None = None,
        infeasible_handling: str = DEFAULT_INFEASIBLE_HANDLING,
        default_penalty: float = DEFAULT_PENALTY_VALUE,
        maximize: bool = True,
        verbose: bool = False,
        population: Population | None = None,
        **kwargs: Any,
    ):
        # Resolve aliases for hyperparameters
        self.ChromosomePrototype: T | None = (
            ChromosomePrototype if ChromosomePrototype is not None else chromosome_prototype
        )
        self.population_size: int = kwargs.get("pop_size", population_size)
        self.TotalGenerations: int = (
            TotalGenerations
            if TotalGenerations is not None
            else (total_generations if total_generations is not None else self.DEFAULT_TOTAL_GENERATIONS)
        )
        self.crossover_probability: float = (
            crossover_probability
            if crossover_probability is not None
            else (crossover_prob if crossover_prob is not None else self.DEFAULT_CROSSOVER_PROBABILITY)
        )
        self.mutation_probability: float = (
            mutation_probability
            if mutation_probability is not None
            else (mutation_prob if mutation_prob is not None else self.DEFAULT_MUTATION_PROBABILITY)
        )
        self.maximize: bool = maximize
        self.verbose: bool = verbose
        self.default_penalty: float = default_penalty

        # Constraint handling and user-provided functions
        self.fitness_function: FitnessFunction | None = fitness_function
        self.feasibility_function: FeasibilityFunction | None = feasibility_function
        self.penalty_function: PenaltyFunction | None = penalty_function
        self.repair_function: RepairFunction | None = repair_function
        self.infeasible_handling: str = infeasible_handling.lower()

        # Operators
        self._custom_selection = selection
        self._custom_crossover = crossover
        self._custom_mutation = mutation
        self._custom_replacement = replacement
        self._setup_operators()

        # Initialize Population & State
        self.current_generation: int = 0
        self.population: list[T] = []
        if population is not None:
            self.population = list(population)
        elif self.ChromosomePrototype is not None:
            self.population = self.GeneratePopulation()

        self.best_chromosome: T | None = None
        self.best_fitness: float = -float('inf') if self.maximize else float('inf')
        self.best_feasible_chromosome: T | None = None
        self.best_feasible_fitness: float = -float('inf') if self.maximize else float('inf')

        # History tracking
        self.fitness_history: list[float] = []
        self.feasible_history: list[float] = []

        # Evaluate initial population if available
        if self.population and self.fitness_function is not None:
            self._update_best_tracking()

    # ==========================================================================
    # Operator Setup & Synchronization
    # ==========================================================================

    def _setup_operators(self) -> None:
        """Sets up default operators based on chromosome prototype if not provided."""
        # Selection
        if self._custom_selection is not None:
            self.selection = self._custom_selection
        else:
            self.selection = TournamentSelection(
                fitness_function=self.evaluate_fitness,
                tournament_size=3,
                maximize=self.maximize,
            )

        # Crossover
        if self._custom_crossover is not None:
            self.crossover = self._custom_crossover
        else:
            size = getattr(self.ChromosomePrototype, "size", 10) if self.ChromosomePrototype else 10
            if isinstance(self.ChromosomePrototype, PermutationChromosome):
                self.crossover = OrderCrossover(
                    crossover_probability=self.crossover_probability,
                    size=size,
                )
            else:
                self.crossover = SinglePointCrossover(
                    crossover_probability=self.crossover_probability,
                    size=size,
                )

        # Mutation
        if self._custom_mutation is not None:
            self.mutation = self._custom_mutation
        else:
            if isinstance(self.ChromosomePrototype, BinaryChromosome):
                self.mutation = FlipMutation(self.mutation_probability)
            elif isinstance(self.ChromosomePrototype, PermutationChromosome):
                self.mutation = SwapMutation(self.mutation_probability)
            elif isinstance(self.ChromosomePrototype, FloatChromosome):
                self.mutation = NonUniformMutation(
                    self.mutation_probability,
                    TotalGenerations=self.TotalGenerations,
                )
            else:
                self.mutation = RandomMutation(self.mutation_probability)

        # Replacement
        if self._custom_replacement is not None:
            self.replacement = self._custom_replacement
        else:
            self.replacement = MixedReplacement(
                fitness_function=self.evaluate_fitness,
                strong=max(1, self.population_size // 2),
                maximize=self.maximize,
            )

        self._sync_operators()

    def _sync_operators(self) -> None:
        """Synchronizes operator parameters with current GA state."""
        if hasattr(self, 'selection') and self.selection is not None:
            self.selection.fitness_function = self.evaluate_fitness
            self.selection.maximize = self.maximize
        if hasattr(self, 'replacement') and self.replacement is not None:
            self.replacement.fitness_function = self.evaluate_fitness
            self.replacement.maximize = self.maximize
        if hasattr(self, 'crossover') and self.crossover is not None:
            self.crossover.crossover_probability = self.crossover_probability
        if hasattr(self, 'mutation') and self.mutation is not None:
            self.mutation.mutation_probability = self.mutation_probability
            self.mutation.TotalGenerations = self.TotalGenerations

    # ==========================================================================
    # User Configuration & Setters
    # ==========================================================================

    def configure(self, **kwargs: Any) -> "GeneticAlgorithm[T]":
        """
        Allows the user to reconfigure any GA hyperparameter or function.

        Example:
            ga.configure(
                population_size=100,
                total_generations=200,
                crossover_probability=0.9,
                mutation_probability=0.05,
                infeasible_handling="penalty",
            )
        """
        if "population_size" in kwargs or "pop_size" in kwargs:
            self.population_size = kwargs.get("population_size", kwargs.get("pop_size"))
        if "total_generations" in kwargs or "TotalGenerations" in kwargs:
            self.TotalGenerations = kwargs.get("total_generations", kwargs.get("TotalGenerations"))
        if "crossover_probability" in kwargs or "crossover_prob" in kwargs:
            self.crossover_probability = kwargs.get("crossover_probability", kwargs.get("crossover_prob"))
        if "mutation_probability" in kwargs or "mutation_prob" in kwargs:
            self.mutation_probability = kwargs.get("mutation_probability", kwargs.get("mutation_prob"))
        if "maximize" in kwargs:
            self.maximize = kwargs["maximize"]
        if "infeasible_handling" in kwargs:
            self.infeasible_handling = kwargs["infeasible_handling"].lower()
        if "default_penalty" in kwargs:
            self.default_penalty = kwargs["default_penalty"]
        if "verbose" in kwargs:
            self.verbose = kwargs["verbose"]
        if "fitness_function" in kwargs:
            self.fitness_function = kwargs["fitness_function"]
        if "feasibility_function" in kwargs:
            self.feasibility_function = kwargs["feasibility_function"]
        if "penalty_function" in kwargs:
            self.penalty_function = kwargs["penalty_function"]
        if "repair_function" in kwargs:
            self.repair_function = kwargs["repair_function"]
        if "ChromosomePrototype" in kwargs or "chromosome_prototype" in kwargs:
            self.ChromosomePrototype = kwargs.get("ChromosomePrototype", kwargs.get("chromosome_prototype"))
        if "selection" in kwargs:
            self._custom_selection = kwargs["selection"]
        if "crossover" in kwargs:
            self._custom_crossover = kwargs["crossover"]
        if "mutation" in kwargs:
            self._custom_mutation = kwargs["mutation"]
        if "replacement" in kwargs:
            self._custom_replacement = kwargs["replacement"]

        self._setup_operators()
        return self

    def set_hyperparameters(
        self,
        population_size: int | None = None,
        total_generations: int | None = None,
        crossover_probability: float | None = None,
        mutation_probability: float | None = None,
        maximize: bool | None = None,
        infeasible_handling: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Updates specific hyperparameters."""
        updates: dict[str, Any] = {}
        if population_size is not None:
            updates["population_size"] = population_size
        if total_generations is not None:
            updates["total_generations"] = total_generations
        if crossover_probability is not None:
            updates["crossover_probability"] = crossover_probability
        if mutation_probability is not None:
            updates["mutation_probability"] = mutation_probability
        if maximize is not None:
            updates["maximize"] = maximize
        if infeasible_handling is not None:
            updates["infeasible_handling"] = infeasible_handling
        updates.update(kwargs)
        self.configure(**updates)

    def get_hyperparameters(self) -> dict[str, Any]:
        """Returns a dictionary of all current hyperparameters."""
        return {
            "population_size": self.population_size,
            "total_generations": self.TotalGenerations,
            "crossover_probability": self.crossover_probability,
            "mutation_probability": self.mutation_probability,
            "maximize": self.maximize,
            "infeasible_handling": self.infeasible_handling,
            "default_penalty": self.default_penalty,
            "verbose": self.verbose,
            "selection": self.selection.__class__.__name__ if self.selection else None,
            "crossover": self.crossover.__class__.__name__ if self.crossover else None,
            "mutation": self.mutation.__class__.__name__ if self.mutation else None,
            "replacement": self.replacement.__class__.__name__ if self.replacement else None,
        }

    def set_fitness_function(self, fitness_function: FitnessFunction) -> None:
        """Allows user to provide or change the fitness evaluation function."""
        self.fitness_function = fitness_function
        self._sync_operators()

    def set_feasibility_function(self, feasibility_function: FeasibilityFunction | None) -> None:
        """Allows user to provide or change the feasibility check function."""
        self.feasibility_function = feasibility_function

    def set_penalty_function(self, penalty_function: PenaltyFunction | None) -> None:
        """Allows user to provide or change the penalty function."""
        self.penalty_function = penalty_function

    def set_repair_function(self, repair_function: RepairFunction | None) -> None:
        """Allows user to provide or change the repair function."""
        self.repair_function = repair_function

    # ==========================================================================
    # Feasibility Check & Fitness Evaluation
    # ==========================================================================

    def is_feasible(self, chromosome: T) -> bool:
        """
        Evaluates whether a chromosome is feasible using the user-provided feasibility check function.
        Returns True if no feasibility check function was provided.
        """
        if self.feasibility_function is None:
            return True
        try:
            return bool(self.feasibility_function(chromosome))
        except (TypeError, AttributeError):
            return bool(self.feasibility_function(chromosome.genes))

    def _call_raw_fitness(self, chromosome: T) -> float:
        """Evaluates raw objective value from user fitness function."""
        if self.fitness_function is None:
            raise ValueError("Fitness function has not been provided. Use set_fitness_function() or pass it in __init__.")
        try:
            return float(self.fitness_function(chromosome))
        except (TypeError, AttributeError):
            return float(self.fitness_function(chromosome.genes))

    def evaluate_fitness(self, chromosome: T) -> float:
        """
        Computes fitness for a given chromosome, handling infeasible solutions
        using the selected constraint handling strategy (penalty, death penalty, repair, reject, deb_rules).
        """
        feasible = self.is_feasible(chromosome)

        if feasible:
            return self._call_raw_fitness(chromosome)

        # ----------------------------------------------------------------------
        # Strategy 1: Repair
        # ----------------------------------------------------------------------
        if self.infeasible_handling == "repair" and self.repair_function is not None:
            try:
                repaired = self.repair_function(chromosome)
            except (TypeError, AttributeError):
                repaired = self.repair_function(chromosome.genes)
            if hasattr(repaired, "genes") and hasattr(chromosome, "genes"):
                chromosome.genes = list(repaired.genes)
            return self._call_raw_fitness(chromosome)

        # ----------------------------------------------------------------------
        # Strategy 2: Death Penalty / Rejection
        # ----------------------------------------------------------------------
        if self.infeasible_handling in ("death_penalty", "reject"):
            return -1e12 if self.maximize else 1e12

        # ----------------------------------------------------------------------
        # Strategy 3: Deb's Constraint Handling Rules
        # ----------------------------------------------------------------------
        if self.infeasible_handling == "deb_rules":
            raw = self._call_raw_fitness(chromosome)
            penalty = self.default_penalty
            if self.penalty_function is not None:
                try:
                    penalty = float(self.penalty_function(chromosome))
                except (TypeError, AttributeError):
                    penalty = float(self.penalty_function(chromosome.genes))
            return (raw - 1e8 - penalty) if self.maximize else (raw + 1e8 + penalty)

        # ----------------------------------------------------------------------
        # Strategy 4: Penalty Method (Default)
        # ----------------------------------------------------------------------
        raw = self._call_raw_fitness(chromosome)
        if self.penalty_function is not None:
            try:
                penalty = float(self.penalty_function(chromosome))
            except (TypeError, AttributeError):
                penalty = float(self.penalty_function(chromosome.genes))
        else:
            penalty = self.default_penalty

        return (raw - penalty) if self.maximize else (raw + penalty)

    # ==========================================================================
    # Population Generation & Solution Retrieval
    # ==========================================================================

    def GeneratePopulation(self) -> Population:
        """Generates the initial population using ChromosomePrototype."""
        if self.ChromosomePrototype is None:
            raise ValueError("ChromosomePrototype is required to generate a population.")

        population: Population = []
        for _ in range(self.population_size):
            chrom = self.ChromosomePrototype.GetRandomChromosome()
            if self.feasibility_function is not None and self.infeasible_handling == "reject":
                attempts = 0
                while not self.is_feasible(chrom) and attempts < 30:
                    chrom = self.ChromosomePrototype.GetRandomChromosome()
                    attempts += 1
            elif self.feasibility_function is not None and self.infeasible_handling == "repair" and self.repair_function:
                if not self.is_feasible(chrom):
                    chrom = self.repair_function(chrom)
            population.append(chrom)

        return population

    def GetBestChromosome(self) -> T | None:
        """Returns the individual with the highest fitness in the current population."""
        if not self.population:
            return None
        if self.maximize:
            return max(self.population, key=self.evaluate_fitness)
        return min(self.population, key=self.evaluate_fitness)

    def get_best_feasible_chromosome(self) -> T | None:
        """Returns the best strictly feasible chromosome discovered during search."""
        return self.best_feasible_chromosome

    def _update_best_tracking(self) -> None:
        """Updates best overall and best feasible chromosome tracking."""
        current_best = self.GetBestChromosome()
        if current_best is not None:
            current_fit = self.evaluate_fitness(current_best)
            is_better = (current_fit > self.best_fitness) if self.maximize else (current_fit < self.best_fitness)
            if is_better or self.best_chromosome is None:
                self.best_chromosome = current_best.clone()
                self.best_fitness = current_fit

        # Check feasible individuals
        feasible_pop = [c for c in self.population if self.is_feasible(c)]
        if feasible_pop:
            if self.maximize:
                best_feas = max(feasible_pop, key=self.evaluate_fitness)
            else:
                best_feas = min(feasible_pop, key=self.evaluate_fitness)
            best_feas_fit = self.evaluate_fitness(best_feas)

            is_better_feas = (
                (best_feas_fit > self.best_feasible_fitness)
                if self.maximize
                else (best_feas_fit < self.best_feasible_fitness)
            )
            if is_better_feas or self.best_feasible_chromosome is None:
                self.best_feasible_chromosome = best_feas.clone()
                self.best_feasible_fitness = best_feas_fit

    # ==========================================================================
    # Main GA Execution Loop
    # ==========================================================================

    def Run(self, generations: int | None = None) -> T | None:
        """
        Executes the Genetic Algorithm for TotalGenerations.

        Returns:
            The best solution found (prioritizing feasible solutions if constraints are present).
        """
        if self.fitness_function is None:
            raise ValueError("Fitness function must be provided before running the Genetic Algorithm.")

        if generations is not None:
            self.TotalGenerations = generations

        if not self.population:
            self.population = self.GeneratePopulation()

        self._sync_operators()
        self._update_best_tracking()

        for generation in range(self.TotalGenerations):
            self.current_generation = generation
            if hasattr(self.mutation, "current_generation"):
                self.mutation.current_generation = generation
            if hasattr(self.mutation, "TotalGenerations"):
                self.mutation.TotalGenerations = self.TotalGenerations

            # Selection
            parents = self.selection.select(self.population, self.population_size)

            # Crossover
            offspring_pairs = self.crossover.crossover(parents)

            # Mutation & Infeasible Handling for Offspring
            mutated_offspring: list[T] = []
            for pair in offspring_pairs:
                for child in pair:
                    mutated = self.mutation.mutate(child.clone())

                    if self.feasibility_function is not None:
                        if self.infeasible_handling == "reject":
                            attempts = 0
                            while not self.is_feasible(mutated) and attempts < 10:
                                mutated = self.mutation.mutate(child.clone())
                                attempts += 1
                        elif self.infeasible_handling == "repair" and self.repair_function is not None:
                            if not self.is_feasible(mutated):
                                mutated = self.repair_function(mutated)

                    mutated_offspring.append(mutated)

            # Replacement
            self.population = self.replacement.replace(self.population, mutated_offspring)

            # Tracking
            self._update_best_tracking()
            self.fitness_history.append(self.best_fitness)
            if self.best_feasible_chromosome is not None:
                self.feasible_history.append(self.best_feasible_fitness)

            if self.verbose and (generation % 20 == 0 or generation == self.TotalGenerations - 1):
                feas_str = f" | Best Feasible: {self.best_feasible_fitness:.2f}" if self.best_feasible_chromosome else ""
                print(f"Gen {generation:4d} | Best Fitness: {self.best_fitness:.2f}{feas_str}")

        # Return best feasible solution if found, otherwise best chromosome
        if self.best_feasible_chromosome is not None:
            return self.best_feasible_chromosome
        return self.best_chromosome
