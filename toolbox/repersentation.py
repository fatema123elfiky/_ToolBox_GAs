import random

class ChromosomeFactory:
    @staticmethod
    def gen_bin_chromosome(length):
        chromosome = []
        for _ in range(length):
            gene=random.randint(0,1)
            chromosome.append(gene)

        return chromosome

    @staticmethod
    def gen_population(size, chromosome_length):
        population = []
        for _ in range(size):
            chromosome = ChromosomeFactory.gen_bin_chromosome(chromosome_length)

            population.append(chromosome)

        return population
