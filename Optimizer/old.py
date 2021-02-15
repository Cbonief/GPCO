from scipy.optimize import minimize

from Converter.BoostHalfBridge import BoostHalfBridgeInverter
from Converter.Components import *
from Converter.auxiliary_functions import *


# Class for the genetic optimizer.
# It initializes with the selected_components, and the features of the desired_converter.
class genetic_optimizer:

    def __init__(self, selected_components, design_features, safety_params):
        self.Switches = []
        self.Diodes = []
        self.Cores = selected_components['Cores']
        self.Cables = selected_components['Cables']
        self.Dissipators = None
        self.Capacitors = []
        self.design_features = design_features
        self.safety_params = safety_params
        self.population = []
        self.population_size = None

        self.preselection(selected_components['Switches'], selected_components['Diodes'],
                          selected_components['Capacitors'])

    # Removes elements from the list that will not under any circumstances, be feasible for the given design features.
    def preselection(self, switches, diodes, capacitors):
        # Preselection of capacitors.
        c = []
        for n in range(0, 4):
            c.append([])
        for capacitor in capacitors:
            if capacitor.Vmax > self.safety_params['Vc'] * self.design_features['Vi'] * 0.42857142857:
                c[0].append(capacitor)
            if capacitor.Vmax > self.safety_params['Vc'] * self.design_features['Vi']:
                c[1].append(capacitor)
            if capacitor.Vmax > self.safety_params['Vc'] * self.design_features['Vo'] / 4:
                c[2].append(capacitor)
                c[3].append(capacitor)
        self.Capacitors = c

        # Preselection of diodes.
        d = []
        for n in range(0, 2):
            d.append([])
        for diode in diodes:
            if diode.Vmax > self.safety_params['Vd'] * self.design_features['Vo']:
                d[0].append(diode)
                d[1].append(diode)
        self.Diodes = d

        # Preselection of switches.
        s = []
        for n in range(0, 2):
            s.append([])
        for switch in switches:
            if switch.Vmax > self.safety_params['Vs'] * self.design_features['Vi'] * 1.42857142857:
                s[0].append(switch)
                s[1].append(switch)
        self.Switches = s

    # Generates a boundary_feasible circuit.
    # Also uses the area feasiblity condition for the inductors and transformer.
    def generate_circuit(self):
        bounds_feasible = False
        while not bounds_feasible:
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
                    a = self.design_features['Vi'] >= self.design_features['Vo']
                    b = n[0] >= n[1]
                    c = self.design_features['Vo'] * 0.3 / self.design_features['Vi'] < (n[1] / float(n[0])) < \
                        self.design_features['Vo'] * 0.7 / self.design_features['Vi']
                    found = ((a and b) or (not a and not b)) and c
                ncond = [np.random.randint(1, 100), np.random.randint(1, 100)]
                transformer = Transformer(core, cables, n, ncond)
                feasible = transformer.is_feasible(self.safety_params['ku']['Transformer'])

            # Builds a feasible entrance inductor.
            feasible = False
            entrance_inductor = None
            while not feasible:
                core = np.random.choice(self.Cores)
                cable = np.random.choice(self.Cables)
                n = np.random.randint(1, 200)
                ncond = np.random.randint(1, 50)
                entrance_inductor = Inductor(core, cable, n, ncond)
                feasible = entrance_inductor.is_feasible(self.safety_params['ku']['EntranceInductor'])

            # Builds a feasible auxiliary inductor.
            feasible = False
            auxiliary_inductor = None
            while not feasible:
                core = np.random.choice(self.Cores)
                cable = np.random.choice(self.Cables)
                n = np.random.randint(1, 200)
                ncond = np.random.randint(1, 50)
                auxiliary_inductor = Inductor(core, cable, n, ncond)
                feasible = auxiliary_inductor.is_feasible(self.safety_params['ku']['AuxiliaryInductor'])

            # dissipators = [np.random.choice(self.Dissipators), np.random.choice(self.Dissipators)]
            new_converter = BoostHalfBridgeInverter(
                transformer,
                entrance_inductor,
                auxiliary_inductor,
                self.design_features,
                switches,
                diodes,
                capacitors,
                self.safety_params
            )

            [_, bounds_feasible] = determine_bounds(new_converter)
        return new_converter

    # Finds the optimal converter for the list of components and design features given.
    def optimize(self, population_size=50, epochs=50, starting_mutation_rate=0.5, mutation_decay_rate=0.01,
                 minimal_mutation_rate=0.1, crossover_rate=0.5, elitist_rate=0.1, kill_rate=0.1, solution_size=2):
        self.population = []
        self.population_size = population_size
        self.population = self.create_population(population_size)
        best_losses = self.design_features['Po'] * np.zeros(solution_size)
        solutions = np.random.choice(self.population, solution_size)

        mutation_rate = starting_mutation_rate

        for epoch in range(0, epochs):
            losses, feasible = self.test_population()
            sorted_indexes, best_losses, solutions = self.sort_population_indexes(solution_size, losses, feasible,
                                                                                  best_losses, solutions)  # Ok
            elite_indexes = sorted_indexes[0:round(self.population_size * elitist_rate)]
            self.kill_population(elite_indexes, kill_rate, feasible)
            self.cross_population(losses, crossover_rate, elite_indexes)
            self.mutate_population(mutation_rate)

            # Updates the mutation rate.
            mutation_rate = mutation_rate - mutation_decay_rate
            if mutation_rate <= minimal_mutation_rate:
                mutation_rate = minimal_mutation_rate
        return solutions

    # Uses the generate converter function to create a population of a given size.
    def create_population(self, population_size):
        population = []
        for index in range(0, self.population_size):
            population.append(self.generate_circuit())
        return population

    # Tests the population and return two arrays, one with the losses and the other with the feasibility.
    def test_population(self):
        feasible = np.zeros(self.population_size, dtype=np.bool)
        losses = np.zeros(self.population_size)
        for index in range(0, self.population_size):
            # print("Testing individual {}".format(index))
            loss, success = optimize_converter(self.population[index])
            feasible[index] = success
            losses[index] = loss
            # print("Losses = {} | Feasible = {}".format(loss, success))
        return [losses, feasible]

    # Sorts the population indexes from best to worst. So population[indexes[0]] is the best circuit. It also finds if
    # there is a solution better than the best found so far, and if so, saves this solution
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
        arr = np.zeros(2 * solution_size)
        arr[0:solution_size] = best_loss
        pop_arr = solution
        size = solution_size
        for index in range(0, solution_size):
            if feasible[sorted_indexes[index]]:
                arr[solution + index] = losses[sorted_indexes[index]]
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

        for index in range(0, round(self.population_size * kill_rate)):
            found = False
            kill_index = 0
            while not found:
                kill_index = np.random(0, self.population_size)
                if kill_index not in elite_indexes:
                    found = True
            self.population[kill_index] = self.generate_circuit()

    def cross_population(self, losses, crossover_rate, elite_indexes):
        rescaled_losses = rescale(losses, [0.01, 0.1], lambda x: 1 / x)
        rescaled_losses = rescaled_losses / sum(rescaled_losses)
        for crossing in range(0, round(self.population_size * crossover_rate)):
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

        if not offspring.Transformer.is_feasible(self.safety_params['ku']['Transformer']):
            offspring.Transformer.recalculate_winding(self.safety_params['ku']['Transformer'], self.design_features)
        if not offspring.EntranceInductor.is_feasible(self.safety_params['ku']['EntranceInductor']):
            offspring.EntranceInductor.recalculate_winding(self.safety_params['ku']['EntranceInductor'])
        if not offspring.AuxiliaryInductor.is_feasible(self.safety_params['ku']['AuxiliaryInductor']):
            offspring.AuxiliaryInductor.recalculate_winding(self.safety_params['ku']['AuxiliaryInductor'])

        return offspring

    def mutate_population(self, mutation_rate):
        x = 2
        # Nada


def optimize_converter(converter, subroutine_iteration=100, epochs=10, algorithm='SLSQP', bounds=None):
    feasible = False
    if bounds is None:
        [bounds, feasible] = determine_bounds(converter)
    else:
        feasible = True

    if feasible:
        best = 1000
        optimization_result = None
        iteration = 0
        while iteration < epochs:
            x0 = find_feasible_point(converter, bounds)
            try:
                solution = minimize(
                    converter.compensated_total_loss,
                    x0,
                    method=algorithm,
                    bounds=bounds,
                    tol=1e-12,
                    options={'maxiter': subroutine_iteration, 'disp': False},
                    constraints={'fun': converter.total_constraint, 'type': 'ineq'}
                )
                if solution.success:
                    print("Loss {} W".format(solution.fun))
                if solution.fun < best and solution.success:
                    best = solution.fun
                    optimization_result = solution
            except ValueError:
                iteration = - 1
            iteration += 1
        if optimization_result:
            return [best, optimization_result.success, optimization_result.x]
        else:
            return [converter.features['Po'] / 10, False, []]
    else:
        return [None, False, []]

# Uses a penalty method to find a feasible point, this feasible point is used as a starting point for the
# numeric optimizer.
def find_feasible_point(converter, bounds=None, return_bounds=False, maxiter=100):
    if bounds is None:
        bounds = determine_bounds(converter)

    found_point = False
    feasible_point = None
    iteration = 0
    while not found_point and iteration < 100:
        x0 = find_feasible_gain_operating_point(converter, bounds)
        sol = minimize(
            converter.total_violation,
            x0,
            method='COBYLA',
            tol=1e-12,
            options={'maxiter': maxiter, 'disp': False},
            constraints={'fun': converter.gain_restriction, 'type': 'ineq'}
        )
        feasible_point = sol.x
        constraints = converter.total_constraint(feasible_point)
        found_point = True
        for constraint in constraints:
            if constraint <= 0:
                found_point = False
    if return_bounds:
        return [feasible_point, bounds]
    else:
        return feasible_point


def find_feasible_gain_operating_point(converter, bounds=None):
    if bounds is None:
        bounds = determine_bounds(converter)

    Po = converter.features['Po']
    Vo = converter.features['Vo']
    Vi = converter.features['Vi']
    n = converter.transformer.Ratio

    x0 = np.array([random_in_range(bounds[0]), random_in_range(bounds[1]), random_in_range(bounds[2])])
    while not gain_restriction_feasibility(converter, x0):
        x0 = np.array([random_in_range(bounds[0]), random_in_range(bounds[1]), random_in_range(bounds[2])])
    # print('Found a gain feasible point x0 = {}'.format(x0))
    return x0


def determine_bounds(converter):
    Dnominal = converter.features['D_Expected']
    Vnominal = converter.features['Vi']
    Po = converter.features['Po']
    Vo = converter.features['Vo']
    Ro = converter.features['Ro']
    n = converter.transformer.Ratio

    gap_width_bound = [1e-4, 3e-2]
    shrinking_factor = 0.2
    frequency_upper_bounds = [
        (2 * converter.entrance_inductor.Penetration_base / converter.entrance_inductor.Cable.Dcu) ** 2,
        (2 * converter.auxiliary_inductor.Penetration_base / converter.auxiliary_inductor.Cable.Dcu) ** 2,
        (2 * converter.transformer.Primary.Penetration_base / converter.transformer.Primary.Cable.Dcu) ** 2,
        (2 * converter.transformer.Secondary.Penetration_base / converter.transformer.Secondary.Cable.Dcu) ** 2,
        1e6
    ]
    frequency_lower_bounds = [
        (((1 - Dnominal) ** 2) / (Vnominal ** 2 * Dnominal)) * Po / (
                    4 * converter.capacitors[0].C * converter.features['dVc1']),
        ((1 - Dnominal) / Vnominal ** 2) * Po / (converter.capacitors[1].C * converter.features['dVc2']),
        Dnominal * Po / (converter.capacitors[2].C * converter.features['dVo_max'] * Vo ** 2),
        (1 - Dnominal) * Po / (converter.capacitors[3].C * converter.features['dVo_max'] * Vo ** 2),
        100
    ]
    frequency_lower_bound = (1 + shrinking_factor) * max(frequency_lower_bounds)
    frequency_upper_bound = (1 - shrinking_factor) * min(frequency_upper_bounds)

    # Entrance Inductance Bound.
    Li_lower_bounds = [
        converter.entrance_inductor.get_inductance(gap_width_bound[1])
    ]
    Li_upper_bounds = [
        Vnominal * converter.features['Bmax'][
            'EntranceInductor'] * converter.entrance_inductor.N * converter.entrance_inductor.Core.Ae / (
                    Po * (1 + converter.features['dIin_max'])),
        converter.entrance_inductor.get_inductance(gap_width_bound[0])
    ]
    Li_lower_bound = (1 + shrinking_factor) * max(Li_lower_bounds)
    Li_upper_bound = (1 - shrinking_factor) * min(Li_upper_bounds)

    # Auxiliary Inductance Bound.
    Lk_lower_bounds = [
        converter.auxiliary_inductor.get_inductance(gap_width_bound[1])
    ]
    Lk_upper_bounds = [
        converter.auxiliary_inductor.get_inductance(gap_width_bound[0])
    ]
    Lk_lower_bound = (1 + shrinking_factor) * max(Lk_lower_bounds)
    Lk_upper_bound = (1 - shrinking_factor) * min(Lk_upper_bounds)

    feasible = not (
                frequency_lower_bound > frequency_upper_bound or Li_lower_bound > Li_upper_bound or Lk_lower_bound > Lk_upper_bound)
    if feasible:
        k1 = lower_fs_lk_bound_constant(converter)
        k2 = upper_fs_lk_bound_constant(converter)
        if k1 > frequency_lower_bound * Lk_lower_bound:
            Lk_lower_bound = (1 + shrinking_factor) * k1 / frequency_lower_bound
        if k2 < frequency_upper_bound * Lk_upper_bound:
            Lk_upper_bound = (1 - shrinking_factor) * k2 / frequency_upper_bound
        feasible = not (
                    frequency_lower_bound > frequency_upper_bound or Li_lower_bound > Li_upper_bound or Lk_lower_bound > Lk_upper_bound)
    bounds = (
    (frequency_lower_bound, frequency_upper_bound), (Li_lower_bound, Li_upper_bound), (Lk_lower_bound, Lk_upper_bound))
    return [bounds, feasible]


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


def random_in_range(bound):
    b = bound[1]
    a = bound[0]
    return (b - a) * np.random.random_sample() + a
