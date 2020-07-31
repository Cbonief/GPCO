from Converter.auxiliary_functions import *

uo = 4*np.pi*1e-4


def SimulateCircuit(obj, X):

    obj.Transformer.Primary.calculate_rca(X[0], 40)
    obj.Transformer.Secondary.calculate_rca(X[0], 40)
    obj.EntranceInductor.calculate_rca(X[0], 40)
    obj.AuxiliaryInductor.calculate_rca(X[0], 40)

    fs = X[0]
    Li = X[1]/1e8
    # lg2 = X[2]
    eff = X[3]
    Lk = X[2]/1e10
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
    Vi = obj.Features['Vi']
    Ro = (Vo ** 2) / obj.Features['Po']
    Vc1 = Vi * D / (1 - D)
    Vc2 = Vi
    n = obj.Transformer.Ratio
    Ipk_pos = 2 * n * Vo / (Ro * (1-D))
    Ipk_neg = -2 * n * Vo / (Ro * D)
    Ipk_pos_1 = 2 * n * Ts * Vo / (Ro * (Ts + t3 - t6))
    Ipk_neg_1 = 2 * n * Ts * Vo / (Ro * (t3 - t6))
    dIin = Vi * D * Ts / Li
    Po = obj.Features['Po']
    Ipk = (Po / (Vi*eff)) + dIin / 2
    Imin = (Po / (Vi*eff)) - dIin / 2
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
        'Iin': (Imin + Ipk)/2,
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
    LkVrms = AuxiliaryInductorVrms(obj, CalculatedValues)
    CalculatedValues['LkVrms'] = LkVrms
    CalculatedValues['BmaxLk'] = LkVrms/(obj.AuxiliaryInductor.Core.Ae*fs*7*obj.AuxiliaryInductor.N)
    # print('BmaxLk = ', CalculatedValues['BmaxLk'])
    return CalculatedValues


def Transformer_Core_Loss(obj, X):
    fs = X[0]
    k1 = obj.Features['Bmax']['Transformer'] ** obj.Transformer.Core.Beta
    k2 = obj.Transformer.Core.Ve*obj.Transformer.Core.Kc
    core_loss = 1e3*k1*k2*(fs**obj.Transformer.Core.Alpha)
    # print("Perdas no núcleo do Trafo = " + str(CoreLoss))
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

    # print("Perdas no primário do Trafo = " + str(cable_loss_primary))
    # print("Perdas no secundário do Trafo = " + str(cable_loss_secondary))
    # print("Perdas nos cabos do Trafo = " + str(cable_loss_total))
    return cable_loss_total

# Atualizada
def EntranceInductor_Core_Loss(obj, X):
    fs = X[0]
    k2 = obj.EntranceInductor.Core.Ve * obj.EntranceInductor.Core.Kc
    DeltaB = obj.CalculatedValues['dBLi']
    k1 = DeltaB ** obj.EntranceInductor.Core.Beta
    CoreLoss = 1e3*k1*k2*(fs ** obj.EntranceInductor.Core.Alpha)
    # print("Perdas no núcleo do Indutor = " + str(CoreLoss))
    return CoreLoss


def EntranceIndutor_Cable_Loss(obj, X):
    harmonics = obj.CalculatedValues['EntranceInductorHarmonics']
    cable_loss = 0
    for n in range(0, len(harmonics)):
        aux = 0.5
        if n == 0:
            aux = 1
        cable_loss += obj.EntranceInductor.get_rca(n) * (harmonics[n] ** 2) * aux
    # print(cable_loss)
    return cable_loss


def AuxiliaryInductor_Core_Loss(obj, X):
    fs = X[0]
    k2 = obj.AuxiliaryInductor.Core.Ve * obj.AuxiliaryInductor.Core.Kc
    bmax = obj.CalculatedValues['BmaxLk']
    k1 = bmax ** obj.AuxiliaryInductor.Core.Beta
    CoreLoss = 1e3 * k1 * k2 * (fs ** obj.AuxiliaryInductor.Core.Alpha)
    # print(CoreLoss)
    return CoreLoss


def AuxiliaryInductor_Cable_Loss(obj, X):
    harmonics = obj.CalculatedValues['TransformerHarmonics']
    cable_loss = 0
    for n in range(0, len(harmonics)):
        aux = 0.5
        if n == 0:
            aux = 1
        cable_loss += obj.AuxiliaryInductor.get_rca(n) * (harmonics[n] ** 2) * aux
    # print(cable_loss)
    return cable_loss

# Verificado
def Capacitor1_Loss(obj, X):
    rse = obj.Capacitors[0].RSE
    Irms = obj.CalculatedValues['C1Irms']
    CapacitorLoss = rse*Irms**2
    #print("Perdas C1 = " + str(CapacitorLoss))
    return CapacitorLoss

# Verificado
def Capacitor2_Loss(obj, X):
    rse = obj.Capacitors[1].RSE
    Irms = obj.CalculatedValues['C2Irms']
    CapacitorLoss = rse*Irms**2
    #print("Perdas C2 = " + str(CapacitorLoss))
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
    Vi = obj.Features['Vi']
    D = obj.Features['D']['Nominal']
    Vs1max = Vi/(1-D)
    SwitchLoss = (1/2)*Is1max*Vs1max*obj.Switches[0].Toff*fs
    #print('Perdas de Comutação S1 ' + str(SwitchLoss))
    SwitchLoss = SwitchLoss + obj.Switches[0].Rdson*S1Irms**2
    #print("Perdas S1 = " + str(SwitchLoss))
    return SwitchLoss

# Verificado
def Switch2_Loss(obj, X):
    fs = X[0]
    Is2max = obj.CalculatedValues['Is2max']
    S2Irms = obj.CalculatedValues['S2Irms']
    Vi = obj.Features['Vi']
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