import unittest
import random
import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from toolbox.Chromosome.Chromosome import (
    BinaryChromosome,
    IntegerChromosome,
    FloatChromosome,
    PermutationChromosome,
)
from toolbox.Selection.Selection import (
    TournamentSelection,
    RouletteWheelSelection,
)
from toolbox.CrossOver.Crossover import (
    SinglePointCrossover,
    MultiPointCrossover,
    UniformCrossover,
    OrderCrossover,
)
from toolbox.Mutation.Mutation import (
    FlipMutation,
    RandomMutation,
    SwapMutation,
    InsertMutation,
    InversionMutation,
    UniformMutation,
    NonUniformMutation,
)
from toolbox.Replacement.Replacement import (
    FullReplacement,
    MixedReplacement,
)
from toolbox.GeneticAlgorithm.Genetic_Algorithm import GeneticAlgorithm
from cvrp.main import (
    cvrp_feasibility_check,
    cvrp_fitness_evaluation,
    cvrp_penalty_function,
    cvrp_repair_function,
    split_chromosome_to_routes,
    route_cost,
    route_demand,
    optimize_single_route_2opt,
    solve_cvrp,
    CAPACITY,
    NUM_VEHICLES,
    DEMANDS,
)


class TestChromosomeRepresentations(unittest.TestCase):
    """Part 1 - Requirement: Three chromosome representations (binary, integer, and floating-point)."""

    def test_binary_chromosome(self):
        chrom = BinaryChromosome(size=8)
        self.assertEqual(len(chrom.genes), 8)
        self.assertTrue(all(g in (0, 1) for g in chrom.genes))
        self.assertTrue(chrom.Validate(chrom.genes))

        # Test invalid genes raise error
        with self.assertRaises(ValueError):
            BinaryChromosome(size=4, genes=[0, 1, 2, 0])

        # Test clone and GetRandomChromosome
        cloned = chrom.clone()
        self.assertEqual(chrom.genes, cloned.genes)
        rnd = chrom.GetRandomChromosome()
        self.assertEqual(len(rnd.genes), 8)

    def test_integer_chromosome(self):
        chrom = IntegerChromosome(size=10, LowerBound=-5, UpperBound=15)
        self.assertEqual(len(chrom.genes), 10)
        self.assertTrue(all(-5 <= g <= 15 for g in chrom.genes))
        self.assertTrue(chrom.Validate(chrom.genes))

        # Test out of bounds
        with self.assertRaises(ValueError):
            IntegerChromosome(size=3, LowerBound=0, UpperBound=10, genes=[5, 12, 3])

    def test_float_chromosome(self):
        chrom = FloatChromosome(size=6, LowerBound=1.5, UpperBound=8.5, AfterPoint=2)
        self.assertEqual(len(chrom.genes), 6)
        self.assertTrue(all(1.5 <= g <= 8.5 for g in chrom.genes))
        self.assertTrue(chrom.Validate(chrom.genes))

        # Negative precision check
        with self.assertRaises(ValueError):
            FloatChromosome(size=3, LowerBound=0.0, UpperBound=1.0, AfterPoint=-1)

    def test_permutation_chromosome(self):
        chrom = PermutationChromosome(size=16, start_gene=1)
        self.assertEqual(len(chrom.genes), 16)
        self.assertEqual(sorted(chrom.genes), list(range(1, 17)))
        self.assertTrue(chrom.Validate(chrom.genes))


class TestSelectionMethods(unittest.TestCase):
    """Part 1 - Requirement: Two selection methods (Tournament and Roulette Wheel)."""

    def setUp(self):
        # 10 individuals with known fitness
        self.population = [BinaryChromosome(size=5, genes=[i % 2] * 5) for i in range(10)]
        self.fitness_func = lambda c: sum(c.genes)

    def test_tournament_selection_maximization(self):
        sel = TournamentSelection(fitness_function=self.fitness_func, tournament_size=3, maximize=True)
        pairs = sel.select(self.population, num_parents=6)
        self.assertEqual(len(pairs), 3)  # 6 parents in 3 pairs
        for p1, p2 in pairs:
            self.assertIsInstance(p1, BinaryChromosome)
            self.assertIsInstance(p2, BinaryChromosome)

    def test_tournament_selection_minimization(self):
        sel = TournamentSelection(fitness_function=self.fitness_func, tournament_size=4, maximize=False)
        pairs = sel.select(self.population, num_parents=4)
        self.assertEqual(len(pairs), 2)

    def test_roulette_wheel_selection_positive_and_negative(self):
        # Test with negative fitness values
        neg_fitness = lambda c: -100 + sum(c.genes)
        sel = RouletteWheelSelection(fitness_function=neg_fitness, maximize=True)
        pairs = sel.select(self.population, num_parents=4)
        self.assertEqual(len(pairs), 2)

        # Test minimization mode
        sel_min = RouletteWheelSelection(fitness_function=self.fitness_func, maximize=False)
        pairs_min = sel_min.select(self.population, num_parents=4)
        self.assertEqual(len(pairs_min), 2)


class TestCrossoverMethods(unittest.TestCase):
    """Part 1 - Requirement: Multi-point crossover and order crossover."""

    def test_multi_point_crossover(self):
        p1 = BinaryChromosome(size=10, genes=[0] * 10)
        p2 = BinaryChromosome(size=10, genes=[1] * 10)
        cx = MultiPointCrossover(crossover_probability=1.0, size=10, NumberOfPoints=2)
        offspring = cx.crossover([(p1, p2)])
        self.assertEqual(len(offspring), 1)
        c1, c2 = offspring[0]
        self.assertEqual(len(c1.genes), 10)
        self.assertEqual(len(c2.genes), 10)

    def test_order_crossover(self):
        p1 = PermutationChromosome(size=8, genes=[1, 2, 3, 4, 5, 6, 7, 8], start_gene=1)
        p2 = PermutationChromosome(size=8, genes=[8, 7, 6, 5, 4, 3, 2, 1], start_gene=1)
        ox = OrderCrossover(crossover_probability=1.0, size=8, StartPoint=2, EndPoint=5)
        offspring = ox.crossover([(p1, p2)])
        c1, c2 = offspring[0]
        self.assertEqual(sorted(c1.genes), list(range(1, 9)))
        self.assertEqual(sorted(c2.genes), list(range(1, 9)))
        # Verify copied slice is preserved
        self.assertEqual(c1.genes[2:6], p1.genes[2:6])
        self.assertEqual(c2.genes[2:6], p2.genes[2:6])


class TestMutationMethods(unittest.TestCase):
    """Part 1 - Requirement: Three mutation methods."""

    def test_flip_mutation(self):
        chrom = BinaryChromosome(size=10, genes=[0] * 10)
        mut = FlipMutation(mutation_probability=1.0)
        mutated = mut.mutate(chrom)
        self.assertEqual(mutated.genes, [1] * 10)

    def test_swap_mutation(self):
        chrom = PermutationChromosome(size=6, genes=[1, 2, 3, 4, 5, 6], start_gene=1)
        mut = SwapMutation(mutation_probability=1.0, Position1=1, Position2=4)
        mutated = mut.mutate(chrom)
        self.assertEqual(mutated.genes, [1, 5, 3, 4, 2, 6])

    def test_inversion_mutation(self):
        chrom = PermutationChromosome(size=6, genes=[1, 2, 3, 4, 5, 6], start_gene=1)
        mut = InversionMutation(mutation_probability=1.0, StartPoint=1, EndPoint=5)
        mutated = mut.mutate(chrom)
        self.assertEqual(mutated.genes, [1, 5, 4, 3, 2, 6])


class TestReplacementMethods(unittest.TestCase):
    """Part 1 - Requirement: Two replacement methods (Full and Mixed)."""

    def setUp(self):
        self.fit = lambda c: sum(c.genes)
        self.pop = [BinaryChromosome(size=4, genes=[0] * 4) for _ in range(5)]
        self.offspring = [BinaryChromosome(size=4, genes=[1] * 4) for _ in range(5)]

    def test_full_replacement(self):
        rep = FullReplacement(fitness_function=self.fit, elitism=1, maximize=True)
        new_pop = rep.replace(self.pop, self.offspring)
        self.assertEqual(len(new_pop), 5)

    def test_mixed_replacement(self):
        rep = MixedReplacement(fitness_function=self.fit, strong=2, maximize=True)
        new_pop = rep.replace(self.pop, self.offspring)
        self.assertEqual(len(new_pop), 5)


class TestGAToolboxFeatures(unittest.TestCase):
    """Part 1 - General Requirements: default hyperparameters, configuration, constraints."""

    def test_hyperparameter_configuration(self):
        prototype = BinaryChromosome(size=10)
        ga = GeneticAlgorithm(
            fitness_function=lambda c: sum(c.genes),
            ChromosomePrototype=prototype,
        )
        self.assertEqual(ga.population_size, GeneticAlgorithm.DEFAULT_POPULATION_SIZE)
        self.assertEqual(ga.TotalGenerations, GeneticAlgorithm.DEFAULT_TOTAL_GENERATIONS)

        # Reconfigure hyperparameters
        ga.configure(population_size=40, total_generations=25, mutation_probability=0.05)
        self.assertEqual(ga.population_size, 40)
        self.assertEqual(ga.TotalGenerations, 25)
        self.assertEqual(ga.mutation_probability, 0.05)

    def test_constraint_handling_modes(self):
        prototype = IntegerChromosome(size=5, LowerBound=0, UpperBound=10)
        # Feasibility check: sum of genes must be <= 20
        feas_check = lambda c: sum(c.genes) <= 20
        fit_eval = lambda c: sum(c.genes)

        for mode in ("penalty", "death_penalty", "deb_rules"):
            ga = GeneticAlgorithm(
                fitness_function=fit_eval,
                feasibility_function=feas_check,
                ChromosomePrototype=prototype,
                population_size=20,
                total_generations=5,
                infeasible_handling=mode,
                maximize=True,
            )
            sol = ga.Run()
            self.assertIsNotNone(sol)


class TestCVRPPart2(unittest.TestCase):
    """Part 2 - CVRP Problem Modeling, Constraint Handling, and Solution Quality."""

    def test_cvrp_split_and_demands(self):
        # Known global optimum permutation:
        opt_genes = [1, 3, 4, 7, 5, 2, 6, 8, 9, 10, 16, 14, 12, 11, 15, 13]
        chrom = PermutationChromosome(size=16, genes=opt_genes, start_gene=1)
        self.assertTrue(cvrp_feasibility_check(chrom))

        is_feas, routes, cost, excess = split_chromosome_to_routes(opt_genes)
        self.assertTrue(is_feas)
        self.assertEqual(len(routes), NUM_VEHICLES)
        self.assertEqual(excess, 0)
        self.assertEqual(cost, 6208)

        # Check vehicle capacity constraints
        for r in routes:
            self.assertLessEqual(route_demand(r), CAPACITY)

    def test_cvrp_repair_function(self):
        # A random permutation is almost certainly infeasible
        p = PermutationChromosome(16, start_gene=1)
        repaired = cvrp_repair_function(p)
        self.assertTrue(cvrp_feasibility_check(repaired))
        self.assertEqual(sorted(repaired.genes), list(range(1, 17)))

    def test_solve_cvrp_with_repair(self):
        # Fast test with repair constraint handling
        best = solve_cvrp(population_size=30, total_generations=10, infeasible_handling="repair", verbose=False)
        self.assertIsNotNone(best)
        self.assertTrue(cvrp_feasibility_check(best))
        is_feas, routes, cost, _ = split_chromosome_to_routes(best.genes)
        self.assertTrue(is_feas)
        self.assertEqual(len(routes), 4)
        for r in routes:
            self.assertLessEqual(route_demand(r), CAPACITY)

    def test_solve_cvrp_with_penalty(self):
        # Standard run with penalty constraint handling
        best = solve_cvrp(population_size=80, total_generations=50, infeasible_handling="penalty", verbose=False)
        self.assertIsNotNone(best)
        self.assertTrue(cvrp_feasibility_check(best))
        is_feas, routes, cost, _ = split_chromosome_to_routes(best.genes)
        self.assertTrue(is_feas)
        self.assertEqual(len(routes), 4)
        for r in routes:
            self.assertLessEqual(route_demand(r), CAPACITY)


if __name__ == "__main__":
    unittest.main()
