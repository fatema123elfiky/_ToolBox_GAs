# Genetic Algorithm Toolbox & Capacitated Vehicle Routing Problem (CVRP)

A modular, object-oriented Genetic Algorithm (GA) toolbox implemented from scratch in pure Python (standard library only), and its application to solve the **Capacitated Vehicle Routing Problem (CVRP)** benchmark without third-party optimization or GA libraries.

---

## Project Structure & Architecture

```
_ToolBox_GAs/
├── toolbox/                         # Part 1: Generic GA Toolbox
│   ├── Chromosome/
│   │   └── Chromosome.py            # Binary, Integer, Float, Permutation representations
│   ├── CrossOver/
│   │   └── Crossover.py             # Multi-point, Order (OX1), Single-point, Uniform
│   ├── Mutation/
│   │   └── Mutation.py              # Flip, Swap, Inversion, Insert, Uniform, Non-Uniform
│   ├── Selection/
│   │   └── Selection.py             # Tournament, Roulette Wheel (with positive/negative scaling)
│   ├── Replacement/
│   │   └── Replacement.py           # Full (with Elitism), Mixed replacement
│   ├── Types/
│   │   └── Types.py                 # Type annotations and function signatures
│   └── GeneticAlgorithm/
│       └── Genetic_Algorithm.py     # Core GA engine with constraint handling & reconfigurability
├── cvrp/                            # Part 2: CVRP Solver
│   └── main.py                      # Problem modeling, DP splitting, feasibility, fitness, runner
├── tests/
│   └── test_assignment.py           # Full test suite covering all requirements (18 unit tests)
├── README.md
└── SC - Assignment 1 [Fall 2026].pdf
```

---

## Assignment Requirements Checklist

### Part 1: GA Toolbox (60 Marks)
- [x] **Three Chromosome Representations**:
  - `BinaryChromosome`: bitstring representations (`0` or `1`).
  - `IntegerChromosome`: integer bounded genes (`LowerBound` to `UpperBound`).
  - `FloatChromosome`: continuous real-valued genes with configurable precision (`AfterPoint`).
  - *(Bonus)* `PermutationChromosome`: sequence of unique elements used for ordering problems.
- [x] **Two Selection Methods**:
  - `TournamentSelection`: selectable tournament size, supports maximization & minimization.
  - `RouletteWheelSelection`: roulette proportional selection with shift-scaling for negative fitness.
- [x] **Crossover Methods**:
  - `MultiPointCrossover`: $N$-point crossover for simple chromosomes.
  - `OrderCrossover` (OX1): order-preserving crossover for permutation representations.
  - *(Bonus)* `SinglePointCrossover` and `UniformCrossover`.
- [x] **Three Mutation Methods**:
  - `FlipMutation`: bit flip for binary chromosomes.
  - `SwapMutation`: exchanges two genes in permutation chromosomes.
  - `InversionMutation`: reverses a subsegment of genes.
  - *(Bonus)* `InsertMutation`, `RandomMutation`, `UniformMutation`, `NonUniformMutation`.
- [x] **Two Replacement Methods**:
  - `FullReplacement`: generational replacement with optional elitism.
  - `MixedReplacement`: preserves top strong individuals and samples remaining weak slots.
- [x] **Toolbox Usability & Constraints**:
  - Modular, object-oriented design using generic types (`Generic[T]`).
  - Implemented using Python standard library (no third-party GA libraries).
  - Configurable default hyperparameters with `ga.configure(**kwargs)`.
  - User-provided `fitness_function`, `feasibility_function`, `penalty_function`, and `repair_function`.
  - Multiple constraint handling strategies: `"penalty"`, `"death_penalty"`, `"repair"`, `"deb_rules"`.

### Part 2: CVRP Problem (40 Marks)
- [x] **Problem Modeling**: Permutation chromosome decoded into vehicle routes via dynamic programming (Prins' Split algorithm).
- [x] **Constraint Handling**: `cvrp_feasibility_check` verifies all 4 vehicles satisfy the capacity limit of 15.
- [x] **Fitness Function**: Evaluates total route distance with penalty addition for infeasible candidates.
- [x] **Output Format**: Formatted to match the standard Google OR-Tools CVRP benchmark output.
- [x] **Solution Quality**: Attains the theoretical benchmark global optimum (**6208m** total distance, 60 total load across 4 vehicles).

---

## How to Run

### 1. Run the CVRP Solver
```bash
python cvrp/main.py
```

### 2. Run the Full Unit Test Suite
```bash
python -m unittest tests/test_assignment.py
```
*(All 18 tests execute and pass in ~1.4 seconds)*
# _ToolBox_GAs

## Architecture

![Toolbox Architecture](imgs/Toolbox.drawio.png)
