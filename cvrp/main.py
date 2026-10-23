import random
import sys
import os

# Ensure the toolbox module is reachable from any working directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from toolbox.Chromosome.Chromosome import PermutationChromosome
from toolbox.GeneticAlgorithm.Genetic_Algorithm import GeneticAlgorithm
from toolbox.CrossOver.Crossover import OrderCrossover
from toolbox.Mutation.Mutation import InversionMutation, SwapMutation
from toolbox.Selection.Selection import TournamentSelection
from toolbox.Replacement.Replacement import MixedReplacement

# ==============================================================================
# CVRP Problem Specification
# Standard Capacitated Vehicle Routing Problem (OR-Tools Benchmark)
# ==============================================================================

DISTANCE_MATRIX = [
    [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
    [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
    [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
    [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
    [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
    [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
    [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
    [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
    [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
    [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
    [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
    [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
    [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
    [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
    [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
    [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
    [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0]
]

DEMANDS = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
VEHICLE_CAPACITY = 15
CAPACITY = VEHICLE_CAPACITY
NUM_VEHICLES = 4
DEPOT = 0

# ==============================================================================
# Helper Functions for Route Cost, Demand, and Local Search
# ==============================================================================

def route_cost(route: list[int]) -> int:
    if not route:
        return 0
    cost = DISTANCE_MATRIX[DEPOT][route[0]]
    for i in range(len(route) - 1):
        cost += DISTANCE_MATRIX[route[i]][route[i + 1]]
    cost += DISTANCE_MATRIX[route[-1]][DEPOT]
    return cost

def route_demand(route: list[int]) -> int:
    return sum(DEMANDS[node] for node in route)

def optimize_single_route_2opt(route: list[int]) -> list[int]:
    best = list(route)
    best_c = route_cost(best)
    improved = True
    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                new_r = best[:i] + best[i:j+1][::-1] + best[j+1:]
                c = route_cost(new_r)
                if c < best_c:
                    best = new_r
                    best_c = c
                    improved = True
                    break
            if improved:
                break
    return best

def split_chromosome_to_routes(genes: list[int]) -> tuple[bool, list[list[int]], int, int]:
    n = len(genes)
    dp = [[float('inf')] * (n + 1) for _ in range(NUM_VEHICLES + 1)]
    parent = [[-1] * (n + 1) for _ in range(NUM_VEHICLES + 1)]
    dp[0][0] = 0

    for v in range(1, NUM_VEHICLES + 1):
        for j in range(1, n + 1):
            cur_demand = 0
            for i in range(j - 1, -1, -1):
                cur_demand += DEMANDS[genes[i]]
                if cur_demand > VEHICLE_CAPACITY:
                    break
                if dp[v - 1][i] < float('inf'):
                    sub_route = genes[i:j]
                    cost = route_cost(sub_route)
                    if dp[v - 1][i] + cost < dp[v][j]:
                        dp[v][j] = dp[v - 1][i] + cost
                        parent[v][j] = i

    if dp[NUM_VEHICLES][n] < float('inf'):
        routes = []
        curr_j = n
        for v in range(NUM_VEHICLES, 0, -1):
            prev_i = parent[v][curr_j]
            routes.append(genes[prev_i:curr_j])
            curr_j = prev_i
        routes.reverse()
        return True, routes, int(dp[NUM_VEHICLES][n]), 0
    else:
        routes = []
        cur_r: list[int] = []
        cur_d = 0
        excess = 0
        for gene in genes:
            d = DEMANDS[gene]
            if len(routes) < NUM_VEHICLES - 1:
                if cur_d + d <= VEHICLE_CAPACITY:
                    cur_r.append(gene)
                    cur_d += d
                else:
                    routes.append(cur_r)
                    cur_r = [gene]
                    cur_d = d
            else:
                cur_r.append(gene)
                cur_d += d
        routes.append(cur_r)
        while len(routes) < NUM_VEHICLES:
            routes.append([])
        for r in routes:
            excess += max(0, route_demand(r) - VEHICLE_CAPACITY)
        tot_d = sum(route_cost(r) for r in routes)
        return False, routes, tot_d, excess

# ==============================================================================
# Toolbox-Required Functions: Feasibility Check, Penalty, and Fitness Evaluation
# ==============================================================================

def cvrp_feasibility_check(chromosome: PermutationChromosome) -> bool:
    is_feasible, _, _, _ = split_chromosome_to_routes(chromosome.genes)
    return is_feasible

def cvrp_penalty_function(chromosome: PermutationChromosome) -> float:
    is_feasible, _, _, excess = split_chromosome_to_routes(chromosome.genes)
    if is_feasible:
        return 0.0
    return float(20000 + 1000 * excess)

def cvrp_fitness_evaluation(chromosome: PermutationChromosome) -> float:
    is_feasible, routes, distance, _ = split_chromosome_to_routes(chromosome.genes)
    if is_feasible:
        opt_routes = [optimize_single_route_2opt(r) for r in routes]
        total_d = sum(route_cost(r) for r in opt_routes)
        return float(-total_d)
    return float(-distance)

# ==============================================================================
# Solution Printer Formatted Exactly as Required
# ==============================================================================

def print_solution(chromosome: PermutationChromosome):
    """Prints the CVRP solution in the exact format shown in the specification."""
    is_feasible, routes, _, _ = split_chromosome_to_routes(chromosome.genes)
    opt_routes = [optimize_single_route_2opt(r) for r in routes]
    total_distance = sum(route_cost(r) for r in opt_routes)
    total_load = sum(route_demand(r) for r in opt_routes)

    print(f"Objective: {total_distance}")
    for vehicle_id, route in enumerate(opt_routes):
        load = 0
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        plan_output += f" {DEPOT} Load({load}) -> "
        for node in route:
            plan_output += f"{node} Load({load}) -> "
            load += DEMANDS[node]
        plan_output += f"{DEPOT} Load({load})\n"
        route_dist = route_cost(route)
        plan_output += f"Distance of the route: {route_dist}m\n"
        plan_output += f"Load of the route: {load}\n"
        print(plan_output)

    print(f"Total Distance of all routes: {total_distance}m")
    print(f"Total Load of all routes: {total_load}\n")
    validate_solution(opt_routes)

def validate_solution(routes):
    expected_customers = set(range(1, 17))
    all_customers = [
        customer
        for route in routes
        for customer in route
    ]

    checks = {
        "Correct number of vehicles": len(routes) == 4,
        "Every customer is visited": set(all_customers) == expected_customers,
        "No duplicate customers": len(all_customers) == len(set(all_customers)),
        "Capacity constraints": all(
            route_demand(route) <= CAPACITY
            for route in routes
        ),
    }

    for check, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {check}")

    if all(checks.values()):
        print("Solution is FEASIBLE!")
    else:
        print("Solution is NOT FEASIBLE!")

# ==============================================================================
# Main Program
# ==============================================================================

def solve_cvrp(
    population_size: int = 80,
    total_generations: int = 150,
    crossover_prob: float = 0.85,
    mutation_prob: float = 0.25,
    tournament_size: int = 3,
    verbose: bool = False,
    infeasible_handling: str = "penalty",
    **hyperparameter_overrides,
):
    prototype = PermutationChromosome(size=16, start_gene=1)
    ga = GeneticAlgorithm[PermutationChromosome](
        fitness_function=cvrp_fitness_evaluation,
        ChromosomePrototype=prototype,
        selection=TournamentSelection(
            fitness_function=cvrp_fitness_evaluation,
            tournament_size=tournament_size,
            maximize=True,
        ),
        crossover=OrderCrossover(
            crossover_probability=crossover_prob,
            size=16,
        ),
        mutation=InversionMutation(
            mutation_probability=mutation_prob,
        ),
        replacement=MixedReplacement(
            fitness_function=cvrp_fitness_evaluation,
            strong=max(1, population_size // 3),
            maximize=True,
        ),
        population_size=population_size,
        total_generations=total_generations,
        feasibility_function=cvrp_feasibility_check,
        penalty_function=cvrp_penalty_function,
        infeasible_handling=infeasible_handling,
        maximize=True,
        verbose=verbose,
    )

    if hyperparameter_overrides:
        ga.configure(**hyperparameter_overrides)

    best_solution = ga.Run()

    if best_solution is not None:
        print_solution(best_solution)
    else:
        print("No solution found.")
    return best_solution

if __name__ == "__main__":
    solve_cvrp()
