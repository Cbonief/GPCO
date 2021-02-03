import time

from matplotlib.pyplot import *

from Converter.BoostHalfBridge import *
from Tests.test_components import *

'Desenvolvido por Carlos Bonifácio Eberhardt Franco'


'Todos os componentes são carregados no arquivo test_components.py'

print('\nConfigurando conversor')

# Parâmetros desejáveis do conversor.
design_features = {
    'Vo': 400,
    'Vi': 17.4,
    'Ro': 1231,
    'Po': 130,
    'Bmax': {'Transformer': 0.15, 'EntranceInductor': 0.3, 'AuxiliaryInductor': 0.15},
    'dIin_max': 0.2,
    'dVo_max': 0.02,
    'dVc1': 0.10,
    'dVc2': 0.10,
    'Jmax': 450*1e4
}

# Parâmetros de segurança.
safety_params = {
    'Vc': 2.0,
    'Vd': 2.0,
    'Id': 2.0,
    'Ic': 2.0,
    'ku': {'Transformer': 0.4, 'EntranceInductor': 0.6, 'AuxiliaryInductor': 0.4}
}

# Cria uma instância do conversor Boost Half-Bridge
converter = BoostHalfBridgeInverter(design_features, safety_params, Trafo, Li, Lk, switches, diodes, capacitors)

# Calcula as perdas do conversor para várias frequências, mas com a mesma indutância de entrada e 
# indutância auxiliar que a utilizada em Knaesel(2018).
Lss = 2.562e-4
uo = 4*np.pi*1e-7
lg = (28**2)*uo*NEE_42_20.Ae/Lss
expected_losses = {
    'Transformer': {'Core': 2.911, 'Primary': 0.718, 'Secondary': 0.82},
    'EntranceInductor': {'Core': 0.036, 'Cable': 2.103},
    'AuxiliaryInductor': {'Core': 0.438, 'Cable': 0.235},
    'Capacitors': {'C1': 0.148, 'C2': 0.181, 'C3': 0.112, 'C4': 0.038},
    'Diode': {'D3': 0.487, 'D4': 0.487},
    'Switches': {'S1': 0.308, 'S2': 0.957}
}
total = 0
for component in expected_losses:
    for lossType in expected_losses[component]:
        total += expected_losses[component][lossType]
expected_losses['Total'] = total

losses, total_loss = converter.compensated_total_loss_separate([50e3, Lss, 1e-6])
error = {}
for component in expected_losses:
    error[component] = {}
    if component != 'Total':
        for lossType in expected_losses[component]:
            expected = expected_losses[component][lossType]
            calculated = losses[component][lossType]
            error[component][lossType] = round(100*(expected - calculated)/expected)
            print("{},{},{} - {} {}%".format(expected, calculated, error[component][lossType], lossType, component))


Bmax = Lss * 7.836 / (converter.entrance_inductor.Core.Ae * converter.entrance_inductor.N)
dB = Lss * 0.747 / (converter.entrance_inductor.Core.Ae * converter.entrance_inductor.N)

expected_values = {
    'Vc3': 218.297,
    'Vc4': 181.496,
    'D': 0.55,'t3': 4.374e-7, 't6': 1.136e-5,
    'Vc1': 21.267, 'Vc2': 17.4,
    'Ipk_pos': 16.239, 'Ipk_neg': -13.286, 'Ipk_pos_1': 16.096, 'Ipk_neg_1': -13.383,
    'Ipk': 7.836, 'Imin': 7.089,'Iin': 7.462,'dIin': 0.747,
    'dBLi': dB, 'BmaxLi': Bmax,
    'Is1max': 9.15,'Is2max': 21.112,
    'TransformerIrms': 8.474,
    'C1Irms': 3.789,'C2Irms': 7.759,
    'S1Irms': 3.789,'S2Irms': 10.715,
    'D3Iavg': 0.325,'D3Irms': 0.557,
    'D4Iavg': 0.325,'D4Irms': 0.508,
    'C3Irms': 0.452, 'C4Irms': 0.38
}

simulation_error = {}
for value in expected_values:
    expected = expected_values[value]
    calculated = converter.calculated_values[value]
    simulation_error[value] = round(100*(expected - calculated)/expected,2)
    print("{},{},{}%,{}".format(expected, calculated,simulation_error[value],value))

print('Erro das Perdas (> 20 %)')
for component in error:
    if component != 'Total':
        for lossType in error[component]:
            if abs(error[component][lossType]) > 10:
                print('Perdas: '+component+'/'+lossType +': '+str(error[component][lossType])+' %')

print('Erro da Simulação (> 20%)')
for var in simulation_error:
    if abs(simulation_error[var]) > 10:
        print('Erro' + var + ':' + str(simulation_error[var])+' %')


number_of_points = 100
f = np.logspace(3, 5, number_of_points)
lossVec = np.zeros(number_of_points)
t = np.zeros(number_of_points)

mean_time = 0
for n in range(0, number_of_points):
    start = time.time() 
    lossVec[n] = converter.compensated_total_loss([f[n], 2.562e-4, 1e-6])
    end = time.time()
    t[n] = end - start
    mean_time += t[n]
mean_time = mean_time/number_of_points

var = 0
for element in t:
    var += (element - mean_time)**2

var = np.sqrt(var)/number_of_points

print('Cada interação demorou em média {} s'.format(mean_time))
print('O desvio padrão foi de {} s'.format(var))




# Plota o gráfico da perda numa escala mono log X.
figure()
axes()
semilogx(f, lossVec)
xlabel('Frequência (Hz)')
ylabel('Perdas (W)')
grid()


show()