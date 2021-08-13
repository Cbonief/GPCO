# Entrance Inductor Restrictions
def dIin_max(converter, X):
    dIin = converter.calculated_values['dIin']
    Iin = converter.calculated_values['Iin']
    res = (converter.features['dIin_max'] * Iin - dIin)
    return res


def bmax_Li(converter, X):
    res = (converter.features['Bmax']['EntranceInductor'] - converter.calculated_values['BmaxLi'])
    return res


def AeAw_Li(converter, X):
    res = converter.entrance_inductor.Core.AeAw - converter.calculated_values[
        'LiIrms'] * converter.entrance_inductor.Ncond * converter.entrance_inductor.Cable.S / (
                      converter.safety_parameters['Jmax'] * converter.safety_parameters['ku EntranceInductor'])
    return res


def JLi(converter, X):
    res = converter.safety_parameters['Jmax'] - converter.calculated_values['LiIrms'] / (
                converter.entrance_inductor.Cable.Scu * converter.entrance_inductor.Ncond)
    return res


# Auxiliary Inductor #
def bmax_Lk(converter, X):
    res = (converter.features['Bmax']['AuxiliaryInductor'] - converter.calculated_values['BmaxLk'])
    return res


def AeAw_Lk(converter, X):
    res = converter.auxiliary_inductor.Core.AeAw - converter.calculated_values[
        'TransformerIrms'] * converter.entrance_inductor.Ncond * converter.auxiliary_inductor.Cable.S / (
                      converter.safety_parameters['Jmax'] * converter.safety_parameters['ku AuxiliaryInductor'])
    return res


def JLk(converter, X):
    res = converter.safety_parameters['Jmax'] - converter.calculated_values['TransformerIrms'] / (
                converter.auxiliary_inductor.Cable.Scu * converter.auxiliary_inductor.Ncond)
    return res



# RESTRIÇÕES DE TEMPERATURA
def temp_diode(diode, converter, X):
    return converter.diodes[diode-1].Tmax - converter.calculated_values['temperature']['D'+str(diode)]


diode_max_temp = []
for i in range(1, 3):
    diode_max_temp.append(lambda converter, x: temp_diode(i, converter, x))


def zvs_restriction(converter, X):
    cs1 = converter.switches[0].Cds
    cs2 = converter.switches[1].Cds
    Po = converter.features['Po']
    Vo = converter.features['Vo']
    Vi = converter.features['Vi']
    Ro = converter.features['Ro']
    D = converter.calculated_values['D']
    n = converter.transformer.Ratio
    k1 = (cs1+cs2)*(Vi/(1-D))**2
    k2 = (2*n*Vo/D + 2*Po/Vi - Vi*D/(2*X[1]*X[0]))**2
    k3 = (2*n*Vo/(Ro*(1-D)) - Po/Vi + Vi*D/(2*X[0]*X[1]))**2
    k4 = max(k1/k2, k1/k3)
    res = X[2] - k4
    return res


def Lk_restriction_s1(converter, Vi, D, L, fs):
    cs1 = converter.switches[0].Cds
    cs2 = cs1
    Po = converter.features['Po']
    Vo = converter.features['Vo']
    Ro = converter.features['Ro']
    n = converter.transformer.Ratio
    k1 = (cs1+cs2)*(Vi/(1-D))**2
    k2 = (2*n*Vo/D + 2*Po/Vi - Vi*D/(2*L*fs))**2

    return k1/k2

def Lk_restriction_s2(converter, Vi, D, L, fs):
    cs1 = converter.switches[0].Cds
    cs2 = cs1
    Po = converter.features['Po']
    Vo = converter.features['Vo']
    Ro = converter.features['Ro']
    n = converter.transformer.Ratio
    k1 = (cs1+cs2)*(Vi/(1-D))**2
    k2 = (2*n*Vo/(Ro*(1-D)) - Po/Vi + Vi*D/(2*L*fs))**2

    return k1/k2


def gain_restriction(converter, x):
    Po = converter.features['Po']
    Vo = converter.features['Vo']
    Vi = converter.features['Vi']
    n = converter.transformer.Ratio

    k1 = 1.16*n**2*Po
    nVi = n*Vi
    k2 = 0.0441*Vo
    LkFs = x[0]*x[2]
    return 100*(-LkFs + 0.8*Vo*(0.147*nVi-k2)/k1)


def gain_restriction_2(converter, x):
    Po = converter.features['Po']
    Vo = converter.features['Vo']
    Vi = converter.features['Vi']
    n = converter.transformer.Ratio

    k1 = 1.16*n**2*Po
    nVi = n*Vi
    k2 = 0.0441*Vo
    LkFs = x[0]*x[2]
    return 100*(LkFs - 1.2*Vo*(0.063*nVi-k2)/k1)

def lower_fs_lk_bound_constant(converter):
    Po = converter.features['Po']
    Vo = converter.features['Vo']
    Vi = converter.features['Vi']
    n = converter.transformer.Ratio

    k1 = 1.16*n**2*Po
    nVi = n*Vi
    k2 = 0.0441*Vo
    return 1.2*Vo*(0.063*nVi-k2)/k1

def upper_fs_lk_bound_constant(converter):
    Po = converter.features['Po']
    Vo = converter.features['Vo']
    Vi = converter.features['Vi']
    n = converter.transformer.Ratio

    k1 = 1.16*n**2*Po
    nVi = n*Vi
    k2 = 0.0441*Vo
    return 0.8*Vo*(0.147*nVi-k2)/k1


def gain_restriction_feasibility(converter, x):
    if gain_restriction(converter, x) > 0 and gain_restriction_2(converter, x) > 0:
        return True

EntranceInductorRestrictions = [dIin_max, bmax_Li, AeAw_Li]
AuxiliaryInductorRestrictions = [bmax_Lk, AeAw_Lk, JLk, zvs_restriction]
#CapacitorRestrictions = [Capacitor1_Loss, Capacitor2_Loss, Capacitor3_Loss, Capacitor4_Loss]
#DiodeRestrictions = [Diode3_Loss, Diode4_Loss]
#SwitchRestrictions = [Switch1_Loss, Switch2_Loss]

Restrictions = []
Restrictions.extend(EntranceInductorRestrictions)
Restrictions.extend(AuxiliaryInductorRestrictions)
Restrictions.append(gain_restriction)
Restrictions.append(gain_restriction_2)

