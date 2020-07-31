import numpy as np
from Converter.BoostHalfBridge import BoostHalfBridgeInverter
from Converter.Components import *

class GeneticOptimizer:

    def __init__(self, switches, diodes, cores, cables, capacitors, circuit_features, safety_params, dissipators = None):
        self.Switches = []
        self.Diodes = []
        self.Cores = cores
        self.Cables = cables
        self.Dissipators = dissipators
        self.Capacitors = []
        self.CircuitFeatures = circuit_features
        self.SafetyParams = safety_params
        self.population = []
        self.population_size = None

        self.preselection(switches, diodes, capacitors)

    # Removes elements from the list that will not under any circuntances, be feasible in the given circuit.
    def preselection(self, switches, diodes, capacitors):

        # Preselection of capacitors.
        c = []
        for n in range(0, 4):
            c.append([])
        for capacitor in capacitors:
            if capacitor.Vmax > self.SafetyParams['Vc1']*max(self.CircuitFeatures['Vi']['Min']*self.CircuitFeatures['D']['Max']/(1-self.CircuitFeatures['D']['Max']), self.CircuitFeatures['Vi']['Max']*self.CircuitFeatures['D']['Min']/(1-self.CircuitFeatures['D']['Min'])):
                c[0].append(capacitor)
            if capacitor.Vmax > self.SafetyParams['Vc2']*self.CircuitFeatures['Vi']['Max']:
                c[1].append(capacitor)
            if capacitor.Vmax > self.SafetyParams['Vco']*self.CircuitFeatures['Vo']/4:
                c[2].append(capacitor)
                c[3].append(capacitor)
        for n in range(0, 4):
            self.Capacitors.append(c[n])

        # Preselection of diodes.
        d = []
        for n in range(0, 2):
            d.append([])
        for diode in diodes:
            if diode.Vmax > self.SafetyParams['Vdo']*self.CircuitFeatures['Vo']:
                d[0].append(capacitor)
                d[1].append(capacitor)
        for n in range(0, 2):
            self.Diodes.append(d[n])

        # Preselection of switches.
        s = []
        for n in range(0, 2):
            s.append([])
        for switch in switches:
            if switch.Vmax > self.SafetyParams['Vs'] * self.CircuitFeatures['Vi']['Max']/(1-self.CircuitFeatures['D']['Min']):
                s[0].append(capacitor)
                s[1].append(capacitor)
        for n in range(0, 2):
            self.Switches.append(s[n])

    def generate_circuit(self):
        # Chooses the switches, capacitors and diodes for the circuit.
        switches = []
        for n in range(0, 2):
            switches.append(np.random.choice(self.Switches[n]))
        capacitors = []
        for n in range(0, 4):
            capacitors.append(np.random.choice(self.Capacitors[n]))
        diodes = []
        for n in range(0, 2):
            diodes.append(np.random.choice(self.Diodes[n]))

        # Builds a feasible transformer.
        feasible = False
        transformer = None
        while not feasible:
            core = np.random.choice(self.Cores)
            cables = [np.random.choice(self.Cables), np.random.choice(self.Cables)]
            found = False
            n = [0, 0]
            while not found:
                n = [np.random.randint(1, 200), np.random.randint(1, 200)]
                a = self.CircuitFeatures['Vi']['Nominal'] >= self.CircuitFeatures['Vo']
                b = n[0] >= n[1]
                found = (a and b) or (not a and not b)
            ncond = [np.random.randint(1, 50), np.random.randint(1, 50)]
            transformer = Transformer(core, cables, n, ncond)
            feasible = transformer.is_feasible(self.SafetyParams['ku']['Transformer'])

        # Builds a feasible entrance inductor.
        feasible = False
        entrance_inductor = None
        while not feasible:
            core = np.random.choice(self.Cores)
            cable = np.random.choice(self.Cables)
            n = np.random.randint(1, 200)
            ncond = np.random.randint(1, 50)
            entrance_inductor = Inductor(core, cable, n, ncond)
            feasible = entrance_inductor.is_feasible(self.SafetyParams['ku']['EntranceInductor'])

        # Builds a feasible auxiliary inductor.
        feasible = False
        auxiliary_inductor = None
        while not feasible:
            core = np.random.choice(self.Cores)
            cable = np.random.choice(self.Cables)
            n = np.random.randint(1, 200)
            ncond = np.random.randint(1, 50)
            auxiliary_inductor = Inductor(core, cable, n, ncond)
            feasible = auxiliary_inductor.is_feasible(self.SafetyParams['ku']['AuxiliaryInductor'])


        # dissipators = [np.random.choice(self.Dissipators), np.random.choice(self.Dissipators)]
        new_circuit = BoostHalfBridgeInverter(transformer, entrance_inductor, auxiliary_inductor, self.CircuitFeatures, switches, diodes, capacitors)
        return new_circuit

    # Ok
    def optimize(self, population_size=50, epochs=50, starting_mutation_rate=0.5, mutation_decay_rate = 0.01, minimal_mutation_rate=0.1, crossover_rate=0.5, elitist_rate=0.1, kill_rate=0.1, solution_size=2):
        self.population = []
        self.population = self.create_population(population_size)
        best_loss = self.CircuitFeatures['Po']*np.zeros(solution_size)
        solution = np.random.choice[self.population, solution_size]

        mutation_rate = starting_mutation_rate

        for epoch in range(0, epochs):
            [losses, feasible] = self.test_population(population_size)                      # Ok
            [sorted_indexes, best_loss, solution] = self.sort_population_idexes(
                population_size, solution_size, losses, feasible, best_loss, solution)      # Ok
            elite_indexes = sorted_indexes[0:round(self.population_size * elitist_rate)]
            self.kill_population(elite_indexes, kill_rate, feasible)                        # Ok
            self.cross_population(losses, crossover_rate, elite_indexes)                    # Ok
            self.mutate_population(mutation_rate)
            mutation_rate = mutation_rate - mutation_decay_rate
            if mutation_rate <= minimal_mutation_rate:
                mutation_rate = minimal_mutation_rate
        return solution

    # Ok
    def create_population(self, population_size):
        self.population_size = population_size
        population = []
        for index in range(0, self.population_size):
            population.append(self.generate_circuit())
        return population

    # Tests the population and return two arrays, one with the losses and the other with the feasibility.
    # Ok
    def test_population(self):
        feasible = np.zeros(self.population_size, dtype=np.bool)
        losses = np.zeros(self.population_size)
        for index in range(0, self.population_size):
            circuit = self.population[index]
            loss = circuit.optimize()
            if circuit.solution_is_feasible():
                feasible[index] = True
            losses[index] = loss
        return [losses, feasible]

    # Sorts the population indexes from best to worst. So population[indexes[0]] is the best circuit. It also finds if
    # there is a solution better than the best found so far, and if so, saves this solution
    # Ok
    def sort_population_indexes(self, solution_size, losses, feasible, best_loss, solution):
        # Sorts the losses
        sorted_indexes = np.zeros(self.population_size, dtype=np.int)
        for index in range(0, self.population_size):
            best = np.Infinity
            for sorting_index in range(index, self.population_size):
                if losses[sorting_index] < best:
                    best = losses[sorting_index]
                    aux = losses[index]
                    losses[index] = losses[sorting_index]
                    losses[sorting_index] = aux
                    sorted_indexes[index] = sorting_index

        # Verifies if a member of the current population is better then one in the Solution vector.
        arr = best_loss
        pop_arr = solution
        size = solution_size
        for index in range(0, solution_size):
            arr.append(losses[sorted_indexes[index]])
            if feasible[sorted_indexes[index]]:
                pop_arr.append(self.population[sorted_indexes[index]])
                size += 1

        for index in range(0, solution_size):
            lowest = arr[-1]
            for j in range(index, size):
                if arr[j] <= lowest:
                    lowest = arr[j]
                    swap = j
            temp1 = arr[swap]
            temp2 = pop_arr[swap]
            arr[swap] = arr[index]
            pop_arr[swap] = pop_arr[index]
            arr[index] = temp1
            pop_arr[index] = temp2

        best_loss = arr[0:solution_size]
        solution = pop_arr[0:solution_size]

        return [sorted_indexes, best_loss, solution]

    def kill_population(self, elite_indexes, kill_rate, feasible):
        for index in range(0, self.population_size):
            if not feasible[index]:
                self.population[index] = self.generate_circuit()

        for index in range(0, round(self.population_size*kill_rate)):
            found = False
            kill_index = 0
            while not found:
                kill_index = np.random(0, self.population_size)
                if kill_index not in elite_indexes:
                    found = True
            self.population[kill_index] = self.generate_circuit()

    def cross_population(self, losses, crossover_rate, elite_indexes):
        rescaled_losses = rescale(losses, [0.01, 0.1], lambda x: 1/x)
        rescaled_losses = rescaled_losses/sum(rescaled_losses)
        for crossing in range(0, round(self.population_size*crossover_rate)):
            parent_index1 = np.random.choice(self.population_size, rescaled_losses)
            parent_index2 = np.random.choice(self.population_size, rescaled_losses)

            found = False
            child_index = 0
            while not found:
                child_index = np.random.choice(self.population_size)
                found = not (child_index in elite_indexes)
            self.population[child_index] = self.cross_over(parent_index1, parent_index2)

    def cross_over(self, parent1, parent2):
        gene_types = ['primary_cable', 'secondary_cable', 'transformer_core', 'primary_winding', 'secondary_winding',
                      'primary_parallel_wires', 'secondary_parallel_wires',
                      'entrance_inductor_cable', 'entrance_inductor_winding',
                      'entrance_inductor_parallel_wires', 'entrance_inductor_inductor_core',
                      'auxiliary_inductor_cable', 'auxiliary_inductor_winding',
                      'auxiliary_inductor_parallel_wires', 'auxiliary_inductor_core'
                      'c1', 'c2', 'c3', 'c4', 'd3', 'd4', 's1', 's2'
                     ]
        gene_types = np.shuffle(gene_types)
        parent2_gene_types = gene_types[0:11]

        offspring = self.population[parent1]

        for gene_type in parent2_gene_types:
            parent2_gene = self.population[parent2].get_parameter(gene_type)
            offspring.set_parameter(gene_type, parent2_gene)

        if not offspring.Transformer.is_feasible(self.SafetyParams['ku']):
            offspring.Transformer.recalculate_winding(self.SafetyParams['ku'], self.CircuitFeatures)
        if not offspring.EntranceInductor.is_feasible(self.SafetyParams['ku']):
            offspring.EntranceInductor.recalculate_winding(self.SafetyParams['ku'])
        if not offspring.AuxiliaryInductor.is_feasible(self.SafetyParams['ku']):
            offspring.AuxiliaryInductor.recalculate_winding(self.SafetyParams['ku'])

        return offspring

    def mutate_population(self, mutation_rate):
        x = 2
        # Nada


def rescale(vector, bounds, function=None):
    xmax = max(vector)
    xmin = min(vector)
    a = (bounds[1] - bounds[0]) / (xmax - xmin)
    b = (xmax * bounds[0] - xmin * bounds[1]) / (xmax - xmin)
    rescaled = np.zeros(np.size(vector))
    for index in range(0, np.size(vector)):
        rescaled[index] = a * vector[index] + b
        if function:
            rescaled[index] = function(rescaled[index])
    return rescaled

def clamp(number, lower_bound, upper_bound=None):
    if number < lower_bound:
        return lower_bound
    if number > upper_bound:
        return upper_bound
    return number