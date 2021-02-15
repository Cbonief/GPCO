from Converter.auxiliary_functions import *


def Transformer_Core_Loss(obj, X):
    fs = X[0]
    k1 = obj.features['Bmax']['Transformer'] ** obj.transformer.Core.Beta
    k2 = obj.transformer.Core.Ve*obj.transformer.Core.Kc
    core_loss = 1e3*k1*k2*(fs**obj.transformer.Core.Alpha)
    return core_loss


# Atualizada
def Transformer_Primary_Cable_Loss(obj, X):
    fs = X[0]
    harmonics = obj.calculated_values['TransformerHarmonics']
    cable_loss_primary = 0

    for n in range(0, len(harmonics)):
        aux = 0.5
        if n == 0:
            aux = 1
        cable_loss_primary += obj.transformer.Primary.get_rca(n)*(harmonics[n]**2)*aux
    return cable_loss_primary

def Transformer_Secondary_Cable_Loss(obj, X):
    fs = X[0]
    harmonics = obj.calculated_values['TransformerHarmonics']
    cable_loss_secondary = 0

    for n in range(0, len(harmonics)):
        aux = 0.5
        if n == 0:
            aux = 0
        cable_loss_secondary += obj.transformer.Secondary.get_rca(n)*((harmonics[n]/obj.transformer.Ratio)**2)*aux
    return cable_loss_secondary

# Atualizada
def EntranceInductor_Core_Loss(obj, X):
    fs = X[0]
    k2 = obj.entrance_inductor.Core.Ve * obj.entrance_inductor.Core.Kc
    dBLi = obj.calculated_values['dBLi']
    k1 = (dBLi/2) ** obj.entrance_inductor.Core.Beta
    core_loss = 1e3*k1*k2*(fs ** obj.entrance_inductor.Core.Alpha)
    return core_loss


def EntranceIndutor_Cable_Loss(obj, X):
    harmonics = obj.calculated_values['EntranceInductorHarmonics']
    cable_loss = 0
    for n in range(0, len(harmonics)):
        aux = 0.5
        if n == 0:
            aux = 1
        cable_loss += obj.entrance_inductor.get_rca(n) * (harmonics[n] ** 2) * aux
    return cable_loss


def AuxiliaryInductor_Core_Loss(obj, X):
    fs = X[0]
    k2 = obj.auxiliary_inductor.Core.Ve * obj.auxiliary_inductor.Core.Kc
    bmax_lk = obj.calculated_values['BmaxLk']
    k1 = bmax_lk ** obj.auxiliary_inductor.Core.Beta
    core_loss = 1e3 * k1 * k2 * (fs ** obj.auxiliary_inductor.Core.Alpha)
    return core_loss


def AuxiliaryInductor_Cable_Loss(obj, X):
    harmonics = obj.calculated_values['TransformerHarmonics']
    cable_loss = 0
    for n in range(0, len(harmonics)):
        aux = 0.5
        if n == 0:
            aux = 1
        cable_loss += obj.auxiliary_inductor.get_rca(n) * (harmonics[n] ** 2) * aux
    return cable_loss

# Verificado
def Capacitor1_Loss(obj, X):
    rse = obj.capacitors[0].RSE
    irms = obj.calculated_values['C1Irms']
    loss = rse*irms**2
    return loss

# Verificado
def Capacitor2_Loss(obj, X):
    rse = obj.capacitors[1].RSE
    irms = obj.calculated_values['C2Irms']
    loss = rse*irms**2
    return loss

# Verificado
def Capacitor3_Loss(obj, X):
    rse = obj.capacitors[2].RSE
    irms = obj.calculated_values['C3Irms']
    loss = rse*irms**2
    return loss

# Verificado
def Capacitor4_Loss(obj, X):
    rse = obj.capacitors[3].RSE
    irms = obj.calculated_values['C4Irms']
    loss = rse*irms**2
    return loss

# Verificado
def Diode3_Loss(obj, X):
    irms = obj.calculated_values['D3Irms']
    iavg = obj.calculated_values['D3Iavg']
    loss = obj.diodes[0].Rt*irms**2 + obj.diodes[0].Vd*iavg
    return loss

# Verificado
def Diode4_Loss(obj, X):
    irms = obj.calculated_values['D4Irms']
    iavg = obj.calculated_values['D4Iavg']
    loss = obj.diodes[1].Rt*irms**2 + obj.diodes[1].Vd*iavg
    return loss

# Verificado
def Switch1_Loss(obj, X):
    fs = X[0]
    imax = obj.calculated_values['Is1max']
    irms = obj.calculated_values['S1Irms']
    Vi = obj.features['Vi']
    D = obj.calculated_values['D']
    vmax = Vi/(1-D)
    loss = (1/2)*imax*vmax*obj.switches[0].Toff*fs + obj.switches[0].Rdson*irms**2
    return loss

# Verificado
def Switch2_Loss(obj, X):
    fs = X[0]
    imax = obj.calculated_values['Is2max']
    irms = obj.calculated_values['S2Irms']
    Vi = obj.features['Vi']
    D = obj.calculated_values['D']
    vmax = Vi / (1 - D)
    loss = (1 / 2) * imax * vmax * obj.switches[1].Toff * fs + obj.switches[1].Rdson*irms**2
    return loss

loss_function_map = {
    'Transformer': {'Core': Transformer_Core_Loss, 'Primary': Transformer_Primary_Cable_Loss, 'Secondary': Transformer_Secondary_Cable_Loss},
    'EntranceInductor': {'Core': EntranceInductor_Core_Loss, 'Cable': EntranceIndutor_Cable_Loss},
    'AuxiliaryInductor': {'Core': AuxiliaryInductor_Core_Loss, 'Cable': AuxiliaryInductor_Cable_Loss},
    'Capacitors': {'C1': Capacitor1_Loss, 'C2': Capacitor2_Loss, 'C3': Capacitor3_Loss, 'C4': Capacitor4_Loss},
    'Diode': {'D3': Diode3_Loss, 'D4': Diode4_Loss},
    'Switches': {'S1': Switch1_Loss, 'S2': Switch2_Loss}
}
