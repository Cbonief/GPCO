from Converter.auxiliary_functions import *


def SimulateCircuit(obj, X):

    obj.Transformer.Primary.calculate_rca(X[0], 40)
    obj.Transformer.Secondary.calculate_rca(X[0], 40)
    obj.EntranceInductor.calculate_rca(X[0], 40)
    obj.AuxiliaryInductor.calculate_rca(X[0], 40)

    fs = X[0]
    Li = X[1]
    Lk = X[2]
    eff = X[3]

    Ts = 1 / fs

    V = vc3_vc4_d(obj, fs, Lk)
    Vc3 = V[0]
    Vc4 = V[1]
    obj.Features['D']['Nominal'] = V[2]
    Vo = Vc3 + Vc4

    CalculatedValues = {
        'Ts': Ts,
        'Vc3': Vc3,
        'Vc4': Vc4,
        'Vo': Vo
    }

    T = t3t6(obj, CalculatedValues)
    t3 = T[0]
    t6 = T[1]
    D = obj.Features['D']['Nominal']
    print(D)
    Po = obj.Features['Po']
    Vi = obj.Features['Vi']['Nominal']
    Ro = obj.Features['Ro']
    Vc1 = Vi * D / (1 - D)
    Vc2 = Vi
    n = obj.Transformer.Ratio


    dIin = Vi * D * Ts / Li
    Iin = (Po / (Vi*eff))
    Ipk = Iin + (dIin / 2)
    Imin = Iin - (dIin / 2)

    Ipk_pos = 2 * n * Vo / (Ro * (1-D))
    Ipk_neg = -2 * n * Vo / (Ro * D)
    Ipk_pos_1 = 2 * n * Ts * Vo / (Ro * (Ts + t3 - t6))
    Ipk_neg_1 = 2 * n * Ts * Vo / (Ro * (t3 - t6))
    

    
    Io = Po / Vo
    dBLi = (Vi * D / (fs * obj.EntranceInductor.N * obj.EntranceInductor.Core.Ae)) / 2
    BmaxLi = Li*Ipk/(obj.EntranceInductor.N*obj.EntranceInductor.Core.Ae)
    Is1max = Ipk_pos - Imin
    Is2max = Ipk - Ipk_neg

    aux = {
        't3': t3,
        't6': t6,
        'Ro': Ro,
        'Vc1': Vc1,
        'Vc2': Vc2,
        'Ipk_pos': Ipk_pos,
        'Ipk_neg': Ipk_neg,
        'Ipk_pos_1': Ipk_pos_1,
        'Ipk_neg_1': Ipk_neg_1,
        'Ipk': Ipk,
        'Imin': Imin,
        'Iin': Iin,
        'Li': Li,
        'Lk': Lk,
        'Io': Io,
        'dBLi': dBLi,
        'BmaxLi': BmaxLi,
        'dIin': dIin,
        'Is1max': Is1max,
        'Is2max': Is2max
    }

    CalculatedValues.update(aux)
    CalculatedValues['TransformerIrms'] = TransformerIRms(obj, CalculatedValues)
    CalculatedValues['C1Irms'] = c1_irms(obj, CalculatedValues)
    CalculatedValues['C2Irms'] = c2_irms(obj, CalculatedValues)
    CalculatedValues['S1Irms'] = s1_irms(obj, CalculatedValues)
    CalculatedValues['S2Irms'] = s2_irms(obj, CalculatedValues)
    CalculatedValues['D3Iavg'] = D3Iavg(obj, CalculatedValues)
    CalculatedValues['D3Irms'] = D3Irms(obj, CalculatedValues)
    CalculatedValues['D4Iavg'] = D4Iavg(obj, CalculatedValues)
    CalculatedValues['D4Irms'] = D4Irms(obj, CalculatedValues)
    CalculatedValues['C3Irms'] = C3Irms(obj, CalculatedValues)
    CalculatedValues['C4Irms'] = C4Irms(obj, CalculatedValues)
    CalculatedValues['TransformerHarmonics'] = TransformerCurrentHarmonics(obj, CalculatedValues)
    CalculatedValues['EntranceInductorHarmonics'] = InputCurrentHarmonics(obj, CalculatedValues)
    CalculatedValues['LiIrms'] = LiIrms(obj, CalculatedValues)
    LkVrms = AuxiliaryInductorVrms(obj, CalculatedValues)
    CalculatedValues['LkVrms'] = LkVrms
    CalculatedValues['BmaxLk'] = LkVrms/(obj.AuxiliaryInductor.Core.Ae*fs*7*obj.AuxiliaryInductor.N)
    return CalculatedValues


def Transformer_Core_Loss(obj, X):
    fs = X[0]
    k1 = obj.Features['Bmax']['Transformer'] ** obj.Transformer.Core.Beta
    k2 = obj.Transformer.Core.Ve*obj.Transformer.Core.Kc
    core_loss = 1e3*k1*k2*(fs**obj.Transformer.Core.Alpha)
    return core_loss


# Atualizada
def Transformer_Cable_Loss(obj, X):
    fs = X[0]

    harmonics = obj.CalculatedValues['TransformerHarmonics']
    cable_loss_primary = 0
    cable_loss_secondary = 0

    for n in range(0, len(harmonics)):
        aux1 = 0.5
        aux2 = aux1
        if n == 0:
            aux1 = 1
            aux2 = 0
        cable_loss_primary += obj.Transformer.Primary.get_rca(n)*(harmonics[n]**2)*aux1
        cable_loss_secondary += obj.Transformer.Secondary.get_rca(n)*((harmonics[n]/obj.Transformer.Ratio)**2)*aux2
    cable_loss_total = cable_loss_primary + cable_loss_secondary
    return cable_loss_total

# Atualizada
def EntranceInductor_Core_Loss(obj, X):
    fs = X[0]
    k2 = obj.EntranceInductor.Core.Ve * obj.EntranceInductor.Core.Kc
    DeltaB = obj.CalculatedValues['dBLi']
    k1 = DeltaB ** obj.EntranceInductor.Core.Beta
    CoreLoss = 1e3*k1*k2*(fs ** obj.EntranceInductor.Core.Alpha)
    return CoreLoss


def EntranceIndutor_Cable_Loss(obj, X):
    harmonics = obj.CalculatedValues['EntranceInductorHarmonics']
    cable_loss = 0
    for n in range(0, len(harmonics)):
        aux = 0.5
        if n == 0:
            aux = 1
        cable_loss += obj.EntranceInductor.get_rca(n) * (harmonics[n] ** 2) * aux
    return cable_loss


def AuxiliaryInductor_Core_Loss(obj, X):
    fs = X[0]
    k2 = obj.AuxiliaryInductor.Core.Ve * obj.AuxiliaryInductor.Core.Kc
    bmax = obj.CalculatedValues['BmaxLk']
    k1 = bmax ** obj.AuxiliaryInductor.Core.Beta
    CoreLoss = 1e3 * k1 * k2 * (fs ** obj.AuxiliaryInductor.Core.Alpha)
    return CoreLoss


def AuxiliaryInductor_Cable_Loss(obj, X):
    harmonics = obj.CalculatedValues['TransformerHarmonics']
    cable_loss = 0
    for n in range(0, len(harmonics)):
        aux = 0.5
        if n == 0:
            aux = 1
        cable_loss += obj.AuxiliaryInductor.get_rca(n) * (harmonics[n] ** 2) * aux
    return cable_loss

# Verificado
def Capacitor1_Loss(obj, X):
    rse = obj.Capacitors[0].RSE
    Irms = obj.CalculatedValues['C1Irms']
    CapacitorLoss = rse*Irms**2
    return CapacitorLoss

# Verificado
def Capacitor2_Loss(obj, X):
    rse = obj.Capacitors[1].RSE
    Irms = obj.CalculatedValues['C2Irms']
    CapacitorLoss = rse*Irms**2
    return CapacitorLoss

# Verificado
def Capacitor3_Loss(obj, X):
    rse = obj.Capacitors[2].RSE
    Irms = obj.CalculatedValues['C3Irms']
    CapacitorLoss = rse*Irms**2
    return CapacitorLoss

# Verificado
def Capacitor4_Loss(obj, X):
    rse = obj.Capacitors[3].RSE
    Irms = obj.CalculatedValues['C4Irms']
    CapacitorLoss = rse*Irms**2
    return CapacitorLoss

# Verificado
def Diode3_Loss(obj, X):
    D3Irms = obj.CalculatedValues['D3Irms']
    D3Iavg = obj.CalculatedValues['D3Iavg']
    DiodeLoss = obj.Diodes[0].Rt*D3Irms**2 + obj.Diodes[0].Vd*D3Iavg
    return DiodeLoss

# Verificado
def Diode4_Loss(obj, X):
    D4Irms = obj.CalculatedValues['D4Irms']
    D4Iavg = obj.CalculatedValues['D4Iavg']
    DiodeLoss = obj.Diodes[1].Rt*D4Irms**2 + obj.Diodes[1].Vd*D4Iavg
    return DiodeLoss

# Verificado
def Switch1_Loss(obj, X):
    fs = X[0]
    Is1max = obj.CalculatedValues['Is1max']
    S1Irms = obj.CalculatedValues['S1Irms']
    Vi = obj.Features['Vi']['Nominal']
    D = obj.Features['D']['Nominal']
    Vs1max = Vi/(1-D)
    SwitchLoss = (1/2)*Is1max*Vs1max*obj.Switches[0].Toff*fs
    SwitchLoss = SwitchLoss + obj.Switches[0].Rdson*S1Irms**2
    return SwitchLoss

# Verificado
def Switch2_Loss(obj, X):
    fs = X[0]
    Is2max = obj.CalculatedValues['Is2max']
    S2Irms = obj.CalculatedValues['S2Irms']
    Vi = obj.Features['Vi']['Nominal']
    D = obj.Features['D']['Nominal']
    Vs2max = Vi / (1 - D)
    SwitchLoss = (1 / 2) * Is2max * Vs2max * obj.Switches[1].Toff * fs
    SwitchLoss = SwitchLoss + obj.Switches[1].Rdson*S2Irms**2
    return SwitchLoss


TransformerLosses = [Transformer_Core_Loss, Transformer_Cable_Loss]
EntranceInductorLosses = [EntranceInductor_Core_Loss, EntranceIndutor_Cable_Loss]
AuxiliaryInductorLosses = [AuxiliaryInductor_Core_Loss, AuxiliaryInductor_Cable_Loss]
CapacitorLosses = [Capacitor1_Loss, Capacitor2_Loss, Capacitor3_Loss, Capacitor4_Loss]
DiodeLosses = [Diode3_Loss, Diode4_Loss]
SwitchLosses = [Switch1_Loss, Switch2_Loss]

# ConverterLosses = []
# ConverterLosses.extend(TransformerLosses)
# ConverterLosses.extend(EntranceInductorLosses)
# ConverterLosses.extend(AuxiliaryInductorLosses)
# ConverterLosses.extend(CapacitorLosses)
# ConverterLosses.extend(DiodeLosses)
# ConverterLosses.extend(SwitchLosses)

ConverterLosses = {
    'Transformer': {'Core': Transformer_Core_Loss, 'Cable': Transformer_Cable_Loss},
    'EntranceInductor': {'Core': EntranceInductor_Core_Loss, 'Cable': EntranceIndutor_Cable_Loss},
    'AuxiliaryInductor': {'Core': AuxiliaryInductor_Core_Loss, 'Cable': AuxiliaryInductor_Cable_Loss},
    'Capacitors': {'C1': Capacitor1_Loss, 'C2': Capacitor2_Loss, 'C3': Capacitor3_Loss, 'C4': Capacitor4_Loss},
    'Diode': {'D3': Diode3_Loss, 'D4': Diode4_Loss},
    'Switches': {'S1': Switch1_Loss, 'S2': Switch2_Loss}
}
