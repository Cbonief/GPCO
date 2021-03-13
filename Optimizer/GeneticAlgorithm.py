import numpy as np

from Optimizer.Genome import Genome

DEFAULT_POPULATION_SIZE = 50

DEFAULT_CONFIG = {
    'Eppchs': 10,
    'Mutation Rate': 0.9,
    'Rewrite Rate': 0.25
}


def get_number_of_decimals(data):
    return len(str(int(100*truncate(data, 2)))) - int(np.ceil(np.log10(data)))


def compose_data(x,y,z):
    result = (10**13)*truncate(x, 2) + (10**16)*get_number_of_decimals(x)
    result += (10**7)*truncate(y, 2) + (10**10)*get_number_of_decimals(y)
    result += z
    result = int(result)
    return str(result)

class GeneticAlgorithm:

    def __init__(self, available_genes, population_size=None):
        if population_size is None:
            population_size = DEFAULT_POPULATION_SIZE
        self.population_size = population_size
        self.available_genes = available_genes
        self.genomes = [None]*population_size
        self.score_sum = 0
        self.avg_score = None
        self.best_score = None
        self.best_score_ever = 0
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

    def optimize(self, evaluation_function, args=None, config=None, numeric_genes_mutation_size=None, progress_function=None):
        self.best_score = np.zeros(config['Epochs'])
        self.avg_score = np.zeros(config['Epochs'])
        if config is None:
            config = DEFAULT_CONFIG
        for epoch in range(0, int(config['Epochs'])):
            self.test_population(epoch, evaluation_function, args)
            self.generate_new_population(config, numeric_genes_mutation_size)
            if progress_function is not None:
                if progress_function[1] is not None:
                    progress_function[0](progress_function[1], [self.best_score[epoch], self.avg_score[epoch], round(100 * (epoch + 1) / config['Epochs'])])
                else:
                    progress_function[0]([self.best_score[epoch], self.avg_score[epoch], epoch])
        return self.fittest_genome

    def test_population(self, epoch, evaluation_function, args=None):
        self.best_score[epoch] = 0
        self.score_sum = 0
        i = 0
        for genome in self.genomes:
            if args:
                genome.score = evaluation_function(genome, epoch, args)
            else:
                genome.score = evaluation_function(genome, epoch)
            self.score_sum += genome.score
            i += 1
            print("Genome {} has score {}".format(i, genome.score))
            if genome.score >= self.best_score[epoch]:
                self.best_score[epoch] = genome.score
            if genome.score >= self.best_score_ever:
                self.best_score_ever = genome.score
                self.fittest_genome = genome
        self.avg_score[epoch] = self.score_sum/self.population_size
        print("Epoch {} Average Score = {}; Best Score = {}".format(epoch, self.avg_score[epoch], self.best_score[epoch]))

    def generate_new_population(self, config, numeric_genes_mutation_size=None):
        if numeric_genes_mutation_size is None:
            numeric_genes_mutation_size = {}
            for key in self.numeric_genes_keys:
                numeric_genes_mutation_size[key] = int(self.available_genes[key][0] / 5)
                if isinstance(self.available_genes[key], int):
                    numeric_genes_mutation_size[key] = int(numeric_genes_mutation_size[key])
        next_generation_genomes = [None]*self.population_size
        next_generation_genomes[0] = self.fittest_genome
        for i in range(1, self.population_size):
            parent1 = self.select_random_genome_biased()
            parent2 = self.select_random_genome_biased()
            child = Genome.crossover(parent1, parent2)
            if np.random.rand() <= config['Mutation Rate']:
                child.mutate(config['Rewrite Rate'], self.available_genes, numeric_genes_mutation_size)
            next_generation_genomes[i] = child

        self.genomes = next_generation_genomes

    def select_random_genome_biased(self):
        threshold = np.random.rand()*self.score_sum
        current_score_sum = 0
        for genome in self.genomes:
            current_score_sum += genome.score
            if current_score_sum >= threshold:
                return genome
        return self.genomes[0]

