from Converter.Restrictions import *
from Converter.Losses import *
from scipy.optimize import minimize
import numpy as np

Losses = []
Losses.extend(TransformerLosses)
Losses.extend(EntranceInductorLosses)
Losses.extend(AuxiliaryInductorLosses)
Losses.extend(CapacitorLosses)
Losses.extend(DiodeLosses)
Losses.extend(SwitchLosses)

Restrictions = [dIin_max, bmax_Li, bmax_Lk]


class BoostHalfBridgeInverter:

    def __init__(self, transformer, entrance_inductor, auxiliary_inductor, circuit_features, switches, diodes, capacitors, dissipators = None):
        self.ConverterLosses = []
        self.CalculatedValues = {}
        for loss in Losses:
            self.ConverterLosses.append({'active': True, 'function': loss})
        self.ConverterRestrictions = []
        for restriction in Restrictions:
            self.ConverterRestrictions.append({'active': True, 'function': restriction, 'type': 'inequation'})
        self.Features = circuit_features
        self.Transformer = transformer
        self.EntranceInductor = entrance_inductor
        self.AuxiliaryInductor = auxiliary_inductor
        self.Capacitors = capacitors
        self.Diodes = diodes
        self.Switches = switches
        self.first_run = True
        self.Dissipators = dissipators
        self.feasibility = False

    def optimize(self, epochs=100, algorithm='SLSQP'):
        self.first_run = True
        x0 = [40e3, 1e8*0.0002562, 1e10*1e-6]
        bounds = ((10e3, 100e3), (1e4, 1e6), (1e10*1e-7, 1e10*1e-5))
        eps = [1e1, 1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8]
        solution = minimize(
                            self.compensated_total_loss,
                            x0,
                            method=algorithm,
                            options={'maxiter': epochs, 'disp': True, 'ftol': 1e-6, 'eps': 1e-4},
                            bounds=bounds,
                            constraints={'fun': self.total_constraint, 'type': 'ineq'}
        )
        print(solution)
        print([solution.x[0], solution.x[1]/1e8, solution.x[2]/1e10])
        self.feasibility = solution.success
        return [solution.x[0], solution.x[1]/1e8, solution.x[2]/1e10]

    def slackness(self, X, rk):
        """Calculates the new objective function, defined by the ALAG Method"""
        slack = self.compensated_total_loss(X)
        for restriction in self.ConverterRestrictions:
            if restriction['type'] is 'eq':
                slack = slack + (restriction['function'](self, X)) ** 2 / rk
            if restriction['type'] is 'inequation':
                slack = slack - np.log(restriction['function'](self, X)) * rk
        return slack

    def compensated_total_loss(self, X):
        """Calculates the total converter loss, iterating to obtain the real efficiency.
        This iteration is due to the fact that the efficiency actually changes the input current of the converter.
        X is a vector containing the frequency, and all the gap widths.
        """
        # print('Called')
        self.Transformer.Primary.calculate_rca(X[0], 40)
        self.Transformer.Secondary.calculate_rca(X[0], 40)
        self.EntranceInductor.calculate_rca(X[0], 40)
        self.AuxiliaryInductor.calculate_rca(X[0], 40)
        efficiency = 0.8
        po = self.Features['Po']
        loss = po * (1 - efficiency) / efficiency
        error = 2
        while error > 0.01:
            loss_last = loss
            loss = self.total_loss([X[0], X[1], X[2], efficiency])
            efficiency = po / (po + loss)
            error = abs(loss_last - loss)
        if self.first_run:
            self.first_run = False
        self.CalculatedValues['efficiency'] = efficiency
        return loss

    def total_loss(self, X):
        """ Calculates the total_loss of the converter, given a frequency, gap widths and efficiency"""
        output = 0
        self.CalculatedValues = SimulateCircuit(self, X)
        for loss in self.ConverterLosses:
            if loss['active']:
                partial = loss['function'](self, X)
                output = output + partial
        return output

    def total_constraint(self, X):
        """ Calculates all the M constraints and returns them in a M sized vector.
            The variable first_run guarantees that you only simulate the circuit in this function if the
            circuit wasn't already simulated in the compensated_total_loss function.
        """
        constraints = []
        eff = 0.8
        if self.first_run:
            self.CalculatedValues = SimulateCircuit(self, [X[0], X[1], X[2], eff])
            self.first_run = False
        else:
            eff = self.CalculatedValues['efficiency']
        for restriction in self.ConverterRestrictions:
            func = restriction['function']
            constraints.append(func(self, [X[0], X[1], X[2], eff], self.CalculatedValues))
        return constraints

    def solution_is_feasible(self):
        return self.feasibility
