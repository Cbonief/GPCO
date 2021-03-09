from Converter.BoostHalfBridge import BoostHalfBridgeInverter
from Converter.Components import *
from Optimizer.Continuous import determine_bounds, optimize_converter
from Optimizer.GeneticAlgorithm import GeneticAlgorithm
from Optimizer.Genome import Genome


# Removes elements from the list that will not under any circumstances, be feasible for the given design features.
def preselection(selected_components, design_features, safety_parameters):
    # Preselection of capacitors.
    capacitors = []
    for n in range(0, 4):
        capacitors.append([])
    for capacitor in selected_components['Capacitors']:
        if capacitor.Vmax > safety_parameters['Vc'] * design_features['Vi'] * 0.42857142857:
            capacitors[0].append(capacitor)
        if capacitor.Vmax > safety_parameters['Vc'] * design_features['Vi']:
            capacitors[1].append(capacitor)
        if capacitor.Vmax > safety_parameters['Vc'] * design_features['Vo'] / 4:
            capacitors[2].append(capacitor)
            capacitors[3].append(capacitor)

    # Preselection of diodes.
    diodes = []
    for n in range(0, 2):
        diodes.append([])
    for diode in selected_components['Diodes']:
        if diode.Vmax > safety_parameters['Vd'] * design_features['Vo']:
            diodes[0].append(diode)
            diodes[1].append(diode)

    # Preselection of switches.
    switches = []
    for n in range(0, 2):
        switches.append([])
    for switch in selected_components['Switches']:
        if switch.Vmax > safety_parameters['Vs'] * design_features['Vi'] * 1.42857142857:
            switches[0].append(switch)
            switches[1].append(switch)
    return capacitors, diodes, switches


def converter_from_genome(genome, design_features, safety_parameters, operating_point=None):
    genes = genome.genes
    transformer = Transformer(genes[0], [genes[1], genes[2]], [genes[3], genes[4]], [genes[5], genes[6]])
    entrance_inductor = Inductor(genes[7], genes[8], genes[9], genes[10])
    auxiliary_inductor = Inductor(genes[11], genes[12], genes[13], genes[14])
    switches = [genes[15], genes[16]]
    diodes = [genes[17], genes[18]]
    capacitors = [genes[19], genes[20], genes[21], genes[22]]
    converter = BoostHalfBridgeInverter(design_features, safety_parameters, transformer, entrance_inductor,
                                        auxiliary_inductor, switches, diodes, capacitors,
                                        operating_point=operating_point)
    return converter


def generate_genome(available_genes, args):
    design_features = args[0]
    safety_parameters = args[1]
    bounds_feasible = False
    transformer = None
    entrance_inductor = None
    capacitors = [None] * 4
    switches = [None] * 2
    diodes = [None] * 2
    auxiliary_inductor = None
    while not bounds_feasible:
        # Chooses the switches, capacitors and diodes for the circuits
        for n in range(0, 2):
            switches[n] = np.random.choice(available_genes['S' + str(n + 1).upper()])
        for n in range(0, 4):
            capacitors[n] = np.random.choice(available_genes['C' + str(n + 1).upper()])
        for n in range(0, 2):
            diodes[n] = np.random.choice(available_genes['D' + str(n + 3).upper()])

        # Builds a feasible transformer.
        feasible = False
        while not feasible:
            core = np.random.choice(available_genes['Transformer Core'])
            cables = [np.random.choice(available_genes['Primary Cable']),
                      np.random.choice(available_genes['Secondary Cable'])]
            found = False
            n = [0, 0]
            while not found:
                n = [np.random.randint(1, 100), np.random.randint(1, 100)]
                a = design_features['Vi'] >= design_features['Vo']
                b = n[0] >= n[1]
                c = design_features['Vo'] * 0.3 / design_features['Vi'] < (n[1] / float(n[0])) < design_features[
                    'Vo'] * 0.7 / design_features['Vi']
                found = ((a and b) or (not a and not b)) and c
            ncond = [np.random.randint(1, 100), np.random.randint(1, 100)]
            transformer = Transformer(core, cables, n, ncond)
            feasible = transformer.is_feasible(safety_parameters['ku Transformer'])

        # Builds a feasible entrance inductor.
        feasible = False
        while not feasible:
            core = np.random.choice(available_genes['Entrance Inductor Core'])
            cable = np.random.choice(available_genes['Entrance Inductor Cable'])
            n = np.random.randint(available_genes['Entrance Inductor N'][0], available_genes['Entrance Inductor N'][1])
            ncond = np.random.randint(available_genes['Entrance Inductor Ncond'][0],
                                      available_genes['Entrance Inductor Ncond'][1])
            entrance_inductor = Inductor(core, cable, n, ncond)
            feasible = entrance_inductor.is_feasible(safety_parameters['ku EntranceInductor'])

        # Builds a feasible auxiliary inductor.
        feasible = False
        while not feasible:
            core = np.random.choice(available_genes['Auxiliary Inductor Core'])
            cable = np.random.choice(available_genes['Auxiliary Inductor Cable'])
            n = np.random.randint(available_genes['Auxiliary Inductor N'][0],
                                  available_genes['Auxiliary Inductor N'][1])
            ncond = np.random.randint(available_genes['Auxiliary Inductor Ncond'][0],
                                      available_genes['Auxiliary Inductor Ncond'][1])
            auxiliary_inductor = Inductor(core, cable, n, ncond)
            feasible = auxiliary_inductor.is_feasible(safety_parameters['ku AuxiliaryInductor'])

        test_converter = BoostHalfBridgeInverter(design_features, safety_parameters, transformer, entrance_inductor,
                                                 auxiliary_inductor, switches, diodes, capacitors)

        [_, bounds_feasible] = determine_bounds(test_converter)

    genes = [
        transformer.Core,
        transformer.Primary.Cable,
        transformer.Secondary.Cable,
        transformer.Primary.N,
        transformer.Secondary.N,
        transformer.Primary.Ncond,
        transformer.Secondary.Ncond,
        entrance_inductor.Core,
        entrance_inductor.Cable,
        entrance_inductor.N,
        entrance_inductor.Ncond,
        auxiliary_inductor.Core,
        auxiliary_inductor.Cable,
        auxiliary_inductor.N,
        auxiliary_inductor.Ncond,
    ]
    genes.extend(switches)
    genes.extend(diodes)
    genes.extend(capacitors)
    new_genome = Genome()
    new_genome.set_genes(genes)
    return new_genome


def evaluate_genome(genome, epoch, features):
    available_genes = features[0]
    design_features = features[1]
    safety_parameters = features[2]
    num_opt_config = features[3]
    converter = converter_from_genome(genome, design_features, safety_parameters)
    if not converter.transformer.is_feasible(safety_parameters['ku Transformer']):
        feasible = False
        core = genome.genes[0]
        cables = [genome.genes[1], genome.genes[2]]
        ncond = []
        n = []
        while not feasible:
            found = False
            n = [0, 0]
            while not found:
                n = [np.random.randint(1, 100), np.random.randint(1, 100)]
                a = design_features['Vi'] >= design_features['Vo']
                b = n[0] >= n[1]
                c = design_features['Vo'] * 0.3 / design_features['Vi'] < (n[1] / float(n[0])) < design_features[
                    'Vo'] * 0.7 / design_features['Vi']
                found = ((a and b) or (not a and not b)) and c
            ncond = [np.random.randint(1, 100), np.random.randint(1, 100)]
            transformer = Transformer(core, cables, n, ncond)
            feasible = transformer.is_feasible(safety_parameters['ku Transformer'])
        genome.genes[3] = n[0]
        genome.genes[4] = n[1]
        genome.genes[5] = ncond[0]
        genome.genes[6] = ncond[1]
    if not converter.entrance_inductor.is_feasible(safety_parameters['ku EntranceInductor']):
        feasible = False
        core = genome.genes[7]
        cable = genome.genes[8]
        n = 1
        ncond = 1
        while not feasible:
            n = np.random.randint(available_genes['Entrance Inductor N'][0], available_genes['Entrance Inductor N'][1])
            ncond = np.random.randint(available_genes['Entrance Inductor Ncond'][0],
                                      available_genes['Entrance Inductor Ncond'][1])
            entrance_inductor = Inductor(core, cable, n, ncond)
            feasible = entrance_inductor.is_feasible(safety_parameters['ku EntranceInductor'])
        genome.genes[9] = n
        genome.genes[10] = ncond
    if not converter.auxiliary_inductor.is_feasible(safety_parameters['ku AuxiliaryInductor']):
        feasible = False
        core = genome.genes[11]
        cable = genome.genes[12]
        n = 1
        ncond = 1
        while not feasible:
            n = np.random.randint(available_genes['Auxiliary Inductor N'][0],
                                  available_genes['Auxiliary Inductor N'][1])
            ncond = np.random.randint(available_genes['Auxiliary Inductor Ncond'][0],
                                      available_genes['Auxiliary Inductor Ncond'][1])
            auxiliary_inductor = Inductor(core, cable, n, ncond)
            feasible = auxiliary_inductor.is_feasible(safety_parameters['ku AuxiliaryInductor'])
        genome.genes[13] = n
        genome.genes[14] = ncond
    [bounds, feasible] = determine_bounds(converter)
    if not feasible:
        return 0
    else:
        iterations = np.ceil(epoch / 20)
        if iterations <= 2:
            iterations = 2
        loss, feasible, x = optimize_converter(converter, bounds=bounds, epochs=iterations)
        genome.set_custom_data(x)
        return design_features['Po'] / loss


GA_DEFAULT_CONFIG = {
    'Population Size': 50,
    'Mutation Rate': 0.9,
    'Epochs': 100,
    'Rewrite Rate': 0.25
}


def optimize_components(selected_components_keys, components_data_base, design_features, safety_parameters,
                        ga_config=None, num_opt_config=None):
    if ga_config is None:
        ga_config = GA_DEFAULT_CONFIG
    selected_components = {}
    for component_type in selected_components_keys:
        selected_components[component_type] = []
        for component_key in selected_components_keys[component_type]:
            selected_components[component_type].append(components_data_base[component_type][component_key])
    selected_components['Capacitors'], selected_components['Diodes'], selected_components['Switches'] = preselection(
        selected_components, design_features, safety_parameters)
    available_genes = {
        'Transformer Core': selected_components['Cores'],
        'Primary Cable': selected_components['Cables'],
        'Secondary Cable': selected_components['Cables'],
        'Primary N': [1, 100],
        'Secondary N': [1, 100],
        'Primary Ncond': [1, 100],
        'Secondary Ncond': [1, 100],
        'Entrance Inductor Core': selected_components['Cores'],
        'Entrance Inductor Cable': selected_components['Cables'],
        'Entrance Inductor N': [1, 100],
        'Entrance Inductor Ncond': [1, 100],
        'Auxiliary Inductor Core': selected_components['Cores'],
        'Auxiliary Inductor Cable': selected_components['Cables'],
        'Auxiliary Inductor N': [1, 100],
        'Auxiliary Inductor Ncond': [1, 100],
        'S1': selected_components['Switches'][0],
        'S2': selected_components['Switches'][1],
        'D3': selected_components['Diodes'][0],
        'D4': selected_components['Diodes'][1],
        'C1': selected_components['Capacitors'][0],
        'C2': selected_components['Capacitors'][1],
        'C3': selected_components['Capacitors'][2],
        'C4': selected_components['Capacitors'][3],
    }

    numeric_genes_mutation_size = {
        'Primary N': 10,
        'Secondary N': 10,
        'Primary Ncond': 5,
        'Secondary Ncond': 5,
        'Entrance Inductor N': 10,
        'Entrance Inductor Ncond': 5,
        'Auxiliary Inductor N': 10,
        'Auxiliary Inductor Ncond': 5
    }

    genetic_algorithm = GeneticAlgorithm(ga_config['Population Size'], available_genes)
    print("Created GA")
    print("Building Initial Population")
    genetic_algorithm.create_population(generate_genome, [design_features, safety_parameters])
    print("Built Initial Population")
    fittest_genome = genetic_algorithm.optimize(
        evaluate_genome,
        [available_genes, design_features, safety_parameters, num_opt_config],
        ga_config['Epochs'],
        ga_config['Mutation Rate'],
        0.2,
        # ga_config['Rewrite Rate'],
        numeric_genes_mutation_size,
    )

    return converter_from_genome(fittest_genome, design_features, safety_parameters, fittest_genome.custom_data)


def threaded_complete_optimization(selected_components_keys, components_data_base, design_features, safety_parameters,
                                   ga_config, num_opt_config, progress_callback):
    print("Thread Started")
    return optimize_components(selected_components_keys, components_data_base, design_features, safety_parameters,
                               ga_config, num_opt_config)


def emit_continuous_optimizer_progress(progress_callback, data):
    progress_callback.emit(data)


def threaded_continuous_optimization(selected_components_keys, components_data_base, Transformer, Li, Lk,
                                     design_features, safety_parameters, num_opt_config, progress_callback):
    capacitors = []
    for i in [1, 2, 3, 4]:
        capacitors.append(components_data_base['Capacitors'][selected_components_keys['C' + str(i)]])
    switches = []
    for i in [1, 2]:
        switches.append(components_data_base['Switches'][selected_components_keys['S' + str(i)]])
    diodes = []
    for i in [3, 4]:
        diodes.append(components_data_base['Diodes'][selected_components_keys['D' + str(i)]])
    converter = BoostHalfBridgeInverter(design_features, safety_parameters, Transformer, Li, Lk, switches, diodes,
                                        capacitors)
    [result, success, output] = optimize_converter(converter, epochs=num_opt_config['Tries'],
                                                   subroutine_iteration=num_opt_config['Iterations'],
                                                   progress_function=emit_continuous_optimizer_progress,
                                                   arg=progress_callback)
    return [result, success, output, converter]
