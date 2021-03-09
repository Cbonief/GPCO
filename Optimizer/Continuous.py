import numpy as np
from scipy.optimize import minimize

from Converter.Restrictions import *


def optimize_converter(converter, subroutine_iteration=100, epochs=2, algorithm='SLSQP', bounds=None,
                       progress_function=None, arg=None):
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
            if x0 is not None:
                try:
                    solution = minimize(
                        converter.compensated_total_loss,
                        x0,
                        method="COBYLA",
                        tol=1e-12,
                        options={'maxiter': subroutine_iteration, 'disp': False},
                        constraints={'fun': converter.total_constraint, 'type': 'ineq'},
                    )
                    if solution.fun < best and solution.success:
                        best = solution.fun
                        optimization_result = solution
                except ValueError:
                    iteration -= 1
                finally:
                    iteration += 1
            if progress_function is not None:
                if arg is not None:
                    progress_function(arg, round(100 * (iteration + 1) / epochs))
                else:
                    progress_function(round(100 * (iteration + 1) / epochs))
        if optimization_result:
            return [best, optimization_result.success, optimization_result.x]
        else:
            return [2 * converter.features['Po'], False, []]
    else:
        return [None, False, []]


# Uses a penalty method to find a feasible point, this feasible point is used as a starting point for the
# numeric optimizer.
def find_feasible_point(converter, bounds=None, return_bounds=False, maxiter=50):
    if bounds is None:
        bounds = determine_bounds(converter)

    found_point = False
    feasible_point = None
    iteration = 0
    while not found_point and iteration < maxiter:
        x0 = find_feasible_gain_operating_point(converter, bounds)
        try:
            sol = minimize(
                converter.total_violation,
                x0,
                method='COBYLA',
                tol=1e-12,
                options={'maxiter': 100, 'disp': False},
                constraints={'fun': converter.total_constraint, 'type': 'ineq'}
            )
            found_point = False
            if sol.success:
                # print("Finished minimizing the violation")
                # print("Verifying Constraints")
                # print(sol)
                found_point = True
            if found_point:
                feasible_point = np.array(sol.x)
        except ValueError:
            iteration -= 1
        finally:
            iteration += 1
    if return_bounds:
        return [feasible_point, bounds]
    else:
        return feasible_point


def find_feasible_gain_operating_point(converter, bounds=None):
    if bounds is None:
        bounds = determine_bounds(converter)

    iteration = 0
    x0 = np.array([random_in_range(bounds[0]), random_in_range(bounds[1]), random_in_range(bounds[2])])
    while not gain_restriction_feasibility(converter, x0) and iteration < 100:
        x0 = np.array([random_in_range(bounds[0]), random_in_range(bounds[1]), random_in_range(bounds[2])])
        iteration += 1
    return x0


def determine_bounds(converter):
    Dnominal = converter.features['D_Expected']
    Vnominal = converter.features['Vi']
    Po = converter.features['Po']
    Vo = converter.features['Vo']

    gap_width_bound = [1e-4, 3e-2]
    shrinking_factor = 0.1
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
