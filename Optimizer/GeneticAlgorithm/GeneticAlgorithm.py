import numpy as np

from Optimizer.GeneticAlgorithm.Genome import Genome


class GeneticAlgorithm:

    def __init__(self, population_size, available_genes):
        self.population_size = population_size
        self.available_genes = available_genes
        self.genomes = [None]*population_size
        self.score_sum = 0
        self.best_score = -np.inf
        self.fittest_genome = None
        self.numeric_genes_keys = []
        for key in available_genes.keys():
            if isinstance(available_genes[key][0], int) or isinstance(available_genes[key][0], float):
                self.numeric_genes_keys.append(key)

    def create_population(self, random_genome_generator_function, args=None):
        for i in range(0, self.population_size):
            if args:
                self.genomes[i] = random_genome_generator_function(self.available_genes, args)
            else:
                self.genomes[i] = random_genome_generator_function(self.available_genes)

    def optimize(self, evaluation_function, args=None, epochs=100, mutation_rate=0.5, rewrite_rate=0.25, numeric_genes_mutation_size=None):
        for epoch in range(0, epochs):
            self.test_population(evaluation_function, args)
            self.generate_new_population(mutation_rate, rewrite_rate, numeric_genes_mutation_size)
        return self.fittest_genome

    def test_population(self, evaluation_function, args=None):
        for genome in self.genomes:
            if args:
                genome.score = evaluation_function(genome, args)
            else:
                genome.score = evaluation_function(genome)
            if genome.score >= self.best_score:
                self.best_score = genome.score
                self.fittest_genome = genome

    def generate_new_population(self, mutation_rate, rewrite_rate, numeric_genes_mutation_size=None):
        if numeric_genes_mutation_size is None:
            numeric_genes_mutation_size = {}
            for key in self.numeric_genes_keys:
                numeric_genes_mutation_size[key] = int(self.available_genes[key][0] / 5)
                if isinstance(self.available_genes[key], int):
                    numeric_genes_mutation_size[key] = int(numeric_genes_mutation_size[key])
        next_generation_genomes = [None]*self.population_size
        next_generation_genomes[0] = self.fittest_genome
        for i in range(1, self.population_size-1):
            parent1 = self.select_random_genome_biased()
            parent2 = self.select_random_genome_biased()
            child = Genome.crossover(parent1, parent2)
            if np.random.rand() <= mutation_rate:
                child.mutate(rewrite_rate, self.available_genes, numeric_genes_mutation_size)
            next_generation_genomes[i] = child
        next_generation_genomes[self.population_size-1] = self.genomes[self.population_size-1]
        self.genomes = next_generation_genomes

    def select_random_genome_biased(self):
        threshold = np.random.rand()*self.score_sum
        current_score_sum = 0
        for genome in self.genomes:
            current_score_sum += genome.score
            if current_score_sum >= threshold:
                return genome

