import numpy as np
from BoostHalfBridge import BoostHalfBridgeInverter
from Components import *

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

    def preselection(self, switches, diodes, cores, cables, capacitors, dissipators = None):

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
        switches = []
        for n in range(0, 2):
            switches.append(np.random.choice(self.Switches[n]))
        capacitors = []
        for n in range(0, 4):
            capacitors.append(np.random.choice(self.Capacitors[n]))
        diodes = []
        for n in range(0, 2):
            diodes.append(np.random.choice(self.Diodes[n]))

        # Constroi o transformador, apenas se ela é possível de fazer.
        feasible = False
        while not feasible:
            core = np.random.choice(self.Cores)
            cables = [np.random.choice(self.Cables), np.random.choice(self.Cables)]
            found = False
            while not found:
                n = [np.random.randint(1, 200), np.random.randint(1, 200)]
                if self.CircuitFeatures['Vi']['Nominal'] > self.CircuitFeatures['Vo']:
                    if n[0] > n[1]:
                        found = True
                else:
                    if n[0] < n[1]:
                        found = True
            ncond = [np.random.randint(1, 50), np.random.randint(1, 50)]
            if (cables[0].S*n[0]*ncond[0] + cables[1].S*n[1]*ncond[1])/self.SafetyParams['ku']['Transfomer'] > core.Aw:
                feasible = True
        transformer = Transformer(core, cables, n, ncond)

        # Constroi o indutor de entrada, apenas se ele for possível.
        feasible = False
        while not feasible:
            core = np.random.choice(self.Cores)
            cable = np.random.choice(self.Cables)
            n = np.random.randint(1, 200)
            ncond = np.random.randint(1, 50)
            if cable.S * n[0] * ncond[0] / self.SafetyParams['ku']['EntranceInductor'] > core.Aw:
                feasible = True
        entrance_inductor = Inductor(core, cable, n, ncond)

        # Constroi o indutor de entrada, apenas se ele for possível.
        feasible = False
        while not feasible:
            core = np.random.choice(self.Cores)
            cable = np.random.choice(self.Cables)
            n = np.random.randint(1, 200)
            ncond = np.random.randint(1, 50)
            if cable.S * n[0] * ncond[0] / self.SafetyParams['ku']['AuxiliaryInductor'] > core.Aw:
                feasible = True
        auxiliary_inductor = Inductor(core, cable, n, ncond)

        # dissipators = [np.random.choice(self.Dissipators), np.random.choice(self.Dissipators)]
        new_circuit = BoostHalfBridgeInverter(transformer, entrance_inductor, auxiliary_inductor, self.CircuitFeatures, switches, diodes, capacitors)
        return new_circuit

    def cross_over_circuits(self):
        return 0

    def optimize(self, population_size=50, epochs=50, mutation_rate=0.1, crossover_rate=0.5, elitist_rate=0.1, kill_rate=0.1, solution_size=2):
        self.population = self.create_population(population_size)
        best_loss = np.zeros(solution_size)
        solution = np.random.choice[self.population, solution_size]

        for epoch in range(0, epochs):
            [losses, feasible] = self.test_population(population_size)
            [sorted_indexes, best_loss, solution] = self.sort_population_idexes(population_size, solution_size, losses, best_loss, solution)
            # Faltar matar os que não funcionaram.
            self.kill_population(population_size, sorted_indexes, elitist_rate, kill_rate, feasible)
            self.cross_population(population_size, losses, sorted_indexes)
        return solution

    def create_population(self, population_size):
        population = []
        for index in range(0,population_size):
            population.append(self.generate_circuit())
        return population

    def test_population(self, population_size):
        feasible = np.zeros(population_size, dtype=np.bool)
        losses = np.zeros(population_size)
        for index in range(0, population_size):
            circuit = self.population[index]
            loss = circuit.optimize()
            if circuit.solution_is_feasible():
                feasible[index] = True
            losses[index] = loss
        return [losses, feasible]
    # Sorts the population indexes from best to worst. So population[indexes[0]] is the best circuit. It also finds if
    # there is a solution better than the best found so far, and if so, saves this solution
    def sort_population_indexes(self, population_size, solution_size, losses, best_loss, solution):
        # Sorts the losses
        sorted_indexes = np.zeros(population_size, dtype=np.int)
        for index in range(0, population_size):
            best = np.Infinity
            for sorting_index in range(index, population_size):
                if losses[sorting_index] < best:
                    best = losses[sorting_index]
                    aux = losses[index]
                    losses[index] = losses[sorting_index]
                    losses[sorting_index] = aux
                    sorted_indexes[index] = sorting_index

        # Verifies if a member of the current population is better then one in the Solution vector.
        finished = False
        done = np.zeros(solution_size, dtype=np.bool)
        index = 0
        while not finished:
            finished = True
            for solution_index in range(0, solution_size):
                if solution_index == 0 and not done[0]:
                    if losses[index] < best_loss[0]:
                        done[0] = True
                        best_loss[solution_index] = losses[index]
                        solution[solution_index] = self.population[sorted_indexes[index]]
                        finished = False
                elif best_loss[solution_index-1] < losses[index] < best_loss[solution_index] and not done[solution_index]:
                    done[solution_index] = True
                    best_loss[solution_index] = losses[index]
                    solution[solution_index] = self.population[sorted_indexes[index]]
                    done[solution_index] = True
                    finished = False
            index = index + 1
        return [sorted_indexes, best_loss, solution]

    def kill_population(self, population_size, sorted_indexes, elitist_rate, kill_rate):
        elit_indexes = sorted_indexes[0:round(population_size*elitist_rate)]
        for index in range(0, round(population_size*kill_rate)):
            found = False
            while not found:
                kill_index = np.random(0,population_size)
                if kill_index not in elit_indexes:
                    found = True
            self.population[kill_index] = self.generate_circuit()

    def cross_population(self, population_size, losses, sorted_indexes):
        return 0
