import numpy as np

from Optimizer.GeneticAlgorithm.GeneticAlgorithm import GeneticAlgorithm
from Optimizer.GeneticAlgorithm.Genome import Genome


# This is file runs a test on the genetic algorithm class.
# The test makes genomes with 3 genes, and rewards them for they're sum being 100.

def random_in_range(bounds):
    return np.random.rand()*(bounds[1]-bounds[0])+bounds[0]


def random_generator(available_genes):
    new_genome = Genome(3)
    genes = [random_in_range(bound) for bound in available_genes.values()]
    new_genome.set_genes(genes)
    return new_genome


genetic_algorithm = GeneticAlgorithm(100, {'x': [-100, 100], 'y': [-10, 10], 'z': [-25, 25]})
genetic_algorithm.create_population(random_generator)


def fitness_function(genome, epoch):
    try:
        return 1/(sum(genome.genes)-100)
    except ZeroDivisionError:
        return np.inf


fittest_genome = genetic_algorithm.optimize(fitness_function, epochs=1000)
print(fittest_genome)
