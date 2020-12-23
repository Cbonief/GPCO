import numpy as np


def random_in_range(bounds):
    return np.random.rand()*(bounds[1]-bounds[0])+bounds[0]


class Genome:

    def __init__(self, genome_size=0, custom_data=None):
        self.size = genome_size
        self.genes = [None] * genome_size
        self.score = 0
        self.custom_data = custom_data

    def set_genes(self, genes):
        self.genes = genes
        self.size = len(genes)

    def mutate(self, rewrite_rate, available_genes, numeric_genes_mutation_size):
        for i, gene_key in zip(range(0, self.size), available_genes.keys()):
            if isinstance(available_genes[gene_key][0], int):
                if np.random.rand() < rewrite_rate:
                    self.genes[i] = np.random.randint(available_genes[gene_key][0], available_genes[gene_key][1])
                else:
                    self.genes[i] += int(random_in_range([-numeric_genes_mutation_size[gene_key], numeric_genes_mutation_size[gene_key]]))
                    if self.genes[i] >= available_genes[gene_key][1]:
                        self.genes[i] = available_genes[gene_key][1]
                    elif self.genes[i] <= available_genes[gene_key][0]:
                        self.genes[i] = available_genes[gene_key][0]
            elif isinstance(available_genes[gene_key][0], float):
                if np.random.rand() < rewrite_rate:
                    self.genes[i] = np.random.rand()*(available_genes[gene_key][1]-available_genes[gene_key][0])+available_genes[gene_key][0]
                else:
                    self.genes[i] += (2*np.random.rand()-1)*numeric_genes_mutation_size[gene_key]
                    if self.genes[i] >= available_genes[gene_key][1]:
                        self.genes[i] = available_genes[gene_key][1]
                    elif self.genes[i] <= available_genes[gene_key][0]:
                        self.genes[i] = available_genes[gene_key][0]
            else:
                if np.random.rand() < rewrite_rate:
                    self.genes[i] = np.random.choice(available_genes)

    def set_custom_data(self, data):
        self.custom_data = data

    @staticmethod
    def crossover(parent1, parent2):
        child = Genome(parent1.size)
        for i in range(0, child.size):
            if np.random.rand() > 0.5:
                child.genes[i] = parent1.genes[i]
            else:
                child.genes[i] = parent2.genes[i]
        return child

    def __repr__(self):
        string = 'Genome with {} elements and score {}\n'.format(self.size, self.score)
        for i in range(0, self.size):
            string += 'Gene[{}] = {}\n'.format(i, self.genes[i])
        return string
