from Optimizer.Continuous import optimize_converter
from test_components import *

'Desenvolvido por Carlos Bonifácio Eberhardt Franco'

'Todos os componentes são carregados no arquivo test_components.py'

print('\nConfigurando conversor')

# Cria uma instância do conversor Boost Half-Bridge
operating_point = np.array([50e3, 2.562e-4, 1e-6])
x = carolina_converter.compensated_total_loss(operating_point)
print("Total Loss at {} is {}".format(operating_point, x))
[result, sucess, output] = optimize_converter(carolina_converter, epochs=10, subroutine_iteration=100)
print([result, sucess, output])
#
# BruteSolution = [
#     32623.17174715356,
#     0.00016890355926438776,
#     3.68127358705167e-08
# ]

# print(converter.compensated_total_loss(BruteSolution))
#
# print(converter)
# [result, sucess, output] = optimize_converter(converter, epochs=100, subroutine_iteration=1000)
#
# print('Solution:')
# print('Fs: {} Hz'.format(output[0]))
# print('Li: {} H'.format(output[1]))
# print('Lk: {} H'.format(output[2]))
#
# print(converter.compensated_total_loss(output))

# output = [
#     30078.270600313954,
#     0.0001798892307692308,
#     3.9207076316800625e-08
# ]
#
# brute_force = [
#     29652.173190796,
#     0.00018370766865114305,
#     4.003930949055375e-08
# ]
#
# error_percentage = [(b-o)/b for b, o in zip(brute_force, output)]
# print(error_percentage)
# print(converter.compensated_total_loss(output))
# print(converter.compensated_total_loss(brute_force))

# best_loss = np.inf
# solution = None
#
# bounds = determine_bounds(converter)
# bounds = bounds[0]
# print(bounds)
# frequency = np.logspace(np.log10(output[0]*0.8), np.log10(output[0]*1.2), 1000)
# Li = np.logspace(np.log10(output[1]*0.5), np.log10(output[1]*2), 100)
# Lk = np.logspace(np.log10(output[2]*0.5), np.log10(output[2]*2), 100)
# for i in range(0, 100):
#     for j in range(0, 100):
#         for k in range(0, 100):
#             try:
#                 loss = converter.compensated_total_loss([frequency[i], Li[i], Lk[i]])
#                 violation = converter.total_violation([frequency[i], Li[i], Lk[i]])
#                 if loss < best_loss and violation == 0.0:
#                     best_loss = loss
#                     solution = [frequency[i], Li[i], Lk[i]]
#                     print(best_loss)
#             except ValueError:
#                 print("valor bosta")
#
#
#
#
# print('Brute Solution:')
# print('Fs: {} Hz'.format(solution[0]))
# print('Li: {} H'.format(solution[1]))
# print('Lk: {} H'.format(solution[2]))