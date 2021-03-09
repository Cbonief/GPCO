import math

import numpy as np

import Converter.Losses as Losses
import Converter.Restrictions as Restrictions
from Converter.Components import Transformer
from Converter.auxiliary_functions import TransformerCurrentHarmonics, D3Iavg, s2_irms, InputCurrentHarmonics, \
    AuxiliaryInductorVrms, D3Irms, s1_irms, TransformerIRms, D4Iavg, c1_irms, C4Irms, vc3_vc4_d, D4Irms, LiIrms, \
    c2_irms, C3Irms


class BoostHalfBridgeInverter:

    def __init__(self, features, safety_params, components, entrance_inductor=None, auxiliary_inductor=None,
                 switches=None, diodes=None, capacitors=None, operating_point=None):
        self.features = features
        self.safety_parameters = safety_params
        self.operating_point = operating_point

        if isinstance(components, Transformer):
            transformer = components
        else:
            transformer = components['Transformer']
            entrance_inductor = components['Entrance Inductor']
            auxiliary_inductor = components['Auxiliary Inductor']
            switches = [components['S1'], components['S2']]
            diodes = [components['D3'], components['D4']]
            capacitors = [components['C1'], components['C2'], components['C3'], components['C4']]

        self.features['D_Expected'] = 1 - (self.features['Vi'] * transformer.Ratio / self.features['Vo'])
        self.features['Ro'] = self.features['Vo'] ** 2 / self.features['Po']
        print(self.features)

        self.loss_functions = Losses.loss_function_map
        self.loss_functions_activation_map = {
            'Transformer': {'Core': True, 'Primary': True, 'Secondary': True},
            'EntranceInductor': {'Core': True, 'Cable': True},
            'AuxiliaryInductor': {'Core': True, 'Cable': True},
            'Capacitors': {'C1': True, 'C2': True, 'C3': True, 'C4': True},
            'Diode': {'D3': True, 'D4': True},
            'Switches': {'S1': True, 'S2': True}
        }

        self.restriction_functions = []
        for restriction in Restrictions.Restrictions:
            self.restriction_functions.append({'active': True, 'function': restriction})
        
        # Componentes
        self.transformer = transformer
        self.entrance_inductor = entrance_inductor
        self.auxiliary_inductor = auxiliary_inductor
        self.capacitors = capacitors
        self.diodes = diodes
        self.switches = switches

        # Variáveis referentes à simulação.
        self.last_calculated_operating_point = [0,0,0]
        self.last_calculated_loss = None
        self.last_calculated_efficiency = None
        self.calculated_values = {}

    # Calculates the total loss of the converter, and it's efficiency.
    # Compensates for the fact that some losses depend of the input current.
    def compensated_total_loss(self, X, activation_table=True, override=False):
        if np.prod(X == self.last_calculated_operating_point, dtype=bool) and not override:
            return self.last_calculated_loss
        else:
            try:
                self.simulate_efficiency_independent_variables(X)
            except ValueError:
                raise ValueError
            efficiency = 0.8
            loss = self.features['Po'] * (1 - efficiency) / efficiency
            error = 2
            while error > 0.1:
                loss_last = loss
                loss = self.total_loss(X, efficiency)
                efficiency = self.features['Po'] / (self.features['Po'] + loss)
                if efficiency <= 0.5:
                    efficiency = 0.5
                error = abs(loss_last - loss)
            if math.isnan(loss) or math.isinf(loss):
                raise ValueError
            else:
                self.last_calculated_loss = loss
                self.last_calculated_efficiency = efficiency
                self.last_calculated_operating_point = X
                return loss

    # Calculates the total loss of the converter, and it's efficiency.
    # Compensates for the fact that some losses depend of the input current.
    def compensated_total_loss_separate(self, X, activation_table=True):
        try:
            self.simulate_efficiency_independent_variables(X)
        except ValueError:
            raise ValueError
        efficiency = 0.8
        total_loss = self.features['Po'] * (1 - efficiency) / efficiency
        error = 2
        losses = None
        while error > 0.1:
            loss_last = total_loss
            losses, total_loss = self.total_loss_separate(X, efficiency)
            efficiency = self.features['Po'] / (self.features['Po'] + total_loss)
            error = abs(loss_last - total_loss)
        return losses, total_loss

    # Calculates the total loss of the converter, for a given estimated efficiency.
    def total_loss(self, X, efficiency):
        output = 0
        self.simulate_efficiency_dependent_variables(X, efficiency)
        for component in self.loss_functions:
            for loss_type in self.loss_functions[component]:
                if self.loss_functions_activation_map[component][loss_type]:
                    partial = self.loss_functions[component][loss_type](self, X)
                    output = output + partial
        return output

    # Same as 'total_loss' but returns a dictonary containing all losses.
    def total_loss_separate(self, X, efficiency):
        losses = {}
        total_loss = 0
        self.simulate_efficiency_dependent_variables(X, efficiency)
        for component in self.loss_functions:
            losses[component] = {}
            for loss_type in self.loss_functions[component]:
                if self.loss_functions_activation_map[component][loss_type]:
                    partial = self.loss_functions[component][loss_type](self, X)
                    losses[component][loss_type] = partial
                    total_loss = total_loss + partial
        return losses, total_loss

    # Calculates all constraints.
    def total_constraint(self, X, get_feasibility=False):
        constraints = []
        # Garantees that the constrains are only calculated if the circuit has been simulated.
        try:
            _ = self.compensated_total_loss(X)
            for restriction in self.restriction_functions:
                func = restriction['function']
                res = func(self, X)
                if math.isnan(res) or math.isinf(res):
                    res = -10
                constraints.append(res)
        except ValueError:
            for i in range(0, len(self.restriction_functions)):
                res = -10
                constraints.append(res)
        return constraints

    # Calculates all constraints and then the violation, and sums them.
    def total_violation(self, X):
        constraints = self.total_constraint(X)
        violation = 0
        for var in constraints:
            violation += max(0, -var)**2
        return violation

    # def violation_of_gain_restriction(self, X):
        

    'SIMULATION'
    def simulate_efficiency_independent_variables(self, X):
        fs = X[0]
        Li = X[1]
        Lk = X[2]

        self.transformer.Primary.calculate_rca(fs, 100)
        self.transformer.Secondary.calculate_rca(fs, 100)
        self.entrance_inductor.calculate_rca(fs, 40)
        self.auxiliary_inductor.calculate_rca(fs, 100)

        Ts = 1 / fs
        # print('fs = {}, Li = {}, Lk = {}'.format(fs,Li,Lk))
        try:
            [Vc3, Vc4, D] = vc3_vc4_d(self, fs, Lk)
        except ValueError:
            raise ValueError

        # print('Vc3 = {}, Vc4 {}, D = {}'.format(Vc3,Vc4, D))
        Vo = Vc3 + Vc4
        if D > 0.7 or D < 0.3:
            print(D)

        calculated_values = {
            'Ts': Ts,
            'Vc3': Vc3,
            'Vc4': Vc4,
            'Vo': Vo,
            'D': D
        }

        Po = self.features['Po']
        Vi = self.features['Vi']
        Ro = self.features['Ro']
        Vc1 = Vi * D / (1 - D)
        Vc2 = Vi
        n = self.transformer.Ratio

        Ipk_pos = 2 * n * Vo / (Ro * (1 - D))
        Ipk_neg = -2 * n * Vo / (Ro * D)

        dIin = Vi * D * Ts / Li

        Io = Po / Vo
        dBLi = Li*dIin/(self.entrance_inductor.N*self.entrance_inductor.Core.Ae)

        aux = {
            'Ro': Ro,
            'Vc1': Vc1,
            'Vc2': Vc2,
            'Ipk_pos': Ipk_pos,
            'Ipk_neg': Ipk_neg,
            'Li': Li,
            'Lk': Lk,
            'Io': Io,
            'dBLi': dBLi,
            'dIin': dIin
        }
        calculated_values.update(aux)

        # Not efficiency dependent.
        LkVrms = AuxiliaryInductorVrms(self, calculated_values)
        calculated_values['TransformerIrms'] = TransformerIRms(self, calculated_values)[0]
        calculated_values['D3Iavg'] = D3Iavg(self, calculated_values)
        calculated_values['D3Irms'] = D3Irms(self, calculated_values)
        calculated_values['D4Iavg'] = D4Iavg(self, calculated_values)
        calculated_values['D4Irms'] = D4Irms(self, calculated_values)
        calculated_values['C3Irms'] = C3Irms(self, calculated_values)
        calculated_values['C4Irms'] = C4Irms(self, calculated_values)
        calculated_values['TransformerHarmonics'] = TransformerCurrentHarmonics(self, calculated_values)
        calculated_values['LkVrms'] = LkVrms
        calculated_values['BmaxLk'] = LkVrms / (self.auxiliary_inductor.Core.Ae * fs * 7 * self.auxiliary_inductor.N)

        self.calculated_values = calculated_values

    def simulate_efficiency_dependent_variables(self, X, efficiency):

        Li = X[1]
        Iin = (self.features['Po'] / (self.features['Vi'] * efficiency))
        dIin = self.calculated_values['dIin']
        Ipk_pos = self.calculated_values['Ipk_pos']
        Ipk_neg = self.calculated_values['Ipk_neg']
        Ipk = Iin + (dIin / 2)
        Imin = Iin - (dIin / 2)
        Is1max = Ipk_pos - Imin
        Is2max = Ipk - Ipk_neg
        BmaxLi = Li*Ipk/(self.entrance_inductor.N*self.entrance_inductor.Core.Ae)
        aux = {
            'Ipk': Ipk,
            'Imin': Imin,
            'Iin': Iin,
            'BmaxLi': BmaxLi,
            'dIin': dIin,
            'Is1max': Is1max,
            'Is2max': Is2max,
            'Efficiency': efficiency
        }
        self.calculated_values.update(aux)
        self.calculated_values['C1Irms'] = c1_irms(self, self.calculated_values)
        self.calculated_values['C2Irms'] = c2_irms(self, self.calculated_values)
        self.calculated_values['S1Irms'] = s1_irms(self, self.calculated_values)
        self.calculated_values['S2Irms'] = s2_irms(self, self.calculated_values)
        self.calculated_values['EntranceInductorHarmonics'] = InputCurrentHarmonics(self, self.calculated_values)
        self.calculated_values['LiIrms'] = LiIrms(self, self.calculated_values)

    def __repr__(self):
        representation = "\n"
        representation += "Converter Boost Half Bridge\n"
        representation += "Transformer\n"
        representation += "- Espiras [{},{}]\n".format(self.transformer.Primary.N, self.transformer.Secondary.N)
        representation += "- Condutores [{},{}]\n".format(self.transformer.Primary.Ncond, self.transformer.Secondary.Ncond)
        representation += "- Cabo [{},{}]\n".format(self.transformer.Primary.Cable.get_name(), self.transformer.Secondary.Cable.get_name())
        representation += "- Núcleo {}\n".format(self.transformer.Core.get_name())
        representation += "Indutor de Entrada\n"
        representation += "- Espiras {}\n".format(self.entrance_inductor.N)
        representation += "- Condutores {}\n".format(self.entrance_inductor.Ncond)
        representation += "- Cabo {}\n".format(self.entrance_inductor.Cable.get_name())
        representation += "- Núcleo {}\n".format(self.entrance_inductor.Core.get_name())
        representation += "Indutor Auxiliar\n"
        representation += "- Espiras: {}\n".format(self.auxiliary_inductor.N)
        representation += "- Condutores: {}\n".format(self.auxiliary_inductor.Ncond)
        representation += "- Cabo: {}\n".format(self.auxiliary_inductor.Cable.get_name())
        representation += "- Núcleo {}\n".format(self.auxiliary_inductor.Core.get_name())
        representation += "Chaves\n"
        representation += "-S1 - {}\n".format(self.switches[0].get_name())
        representation += "-S2 - {}\n".format(self.switches[1].get_name())
        representation += "Capacitores\n"
        representation += "-C1 - {}\n".format(self.capacitors[0].get_name())
        representation += "-C2 - {}\n".format(self.capacitors[1].get_name())
        representation += "-C3 - {}\n".format(self.capacitors[2].get_name())
        representation += "-C4 - {}\n".format(self.capacitors[3].get_name())
        representation += "Diodos\n"
        representation += "-D3 - {}\n".format(self.diodes[0].get_name())
        representation += "-D4 - {}\n".format(self.diodes[1].get_name())
        return representation

    def get_simulated_values(self):
        return self.calculated_values

    def gain_restriction(self, x):
        return [Restrictions.gain_restriction(self, x), Restrictions.gain_restriction_2(self, x)]
