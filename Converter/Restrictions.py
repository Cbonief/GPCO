# Entrance Inductor Restrictions
def dIin_max(obj, X):
    dIin = obj.calculated_values['dIin']
    Iin = obj.calculated_values['Iin']
    res = (obj.features['dIin_max'] * Iin - dIin)
    return res


def bmax_Li(obj, X):
    res = (obj.features['Bmax']['EntranceInductor'] - obj.calculated_values['BmaxLi'])
    return res


def AeAw_Li(obj, X):
    res = obj.entrance_inductor.Core.AeAw - obj.calculated_values[
        'LiIrms'] * obj.entrance_inductor.Ncond * obj.entrance_inductor.Cable.S / (
                      obj.safety_parameters['Jmax'] * obj.safety_parameters['ku EntranceInductor'])
    return res


def JLi(obj, X):
    res = obj.safety_parameters['Jmax'] - obj.calculated_values['LiIrms'] / (
                obj.entrance_inductor.Cable.Scu * obj.entrance_inductor.Ncond)
    print(obj.calculated_values['LiIrms'] / (obj.entrance_inductor.Cable.Scu * obj.entrance_inductor.Ncond),
          obj.safety_parameters['Jmax'])
    return res


# Auxiliary Inductor #
def bmax_Lk(obj, X):
    res = (obj.features['Bmax']['AuxiliaryInductor'] - obj.calculated_values['BmaxLk'])
    return res


def AeAw_Lk(obj, X):
    res = obj.auxiliary_inductor.Core.AeAw - obj.calculated_values[
        'TransformerIrms'] * obj.entrance_inductor.Ncond * obj.auxiliary_inductor.Cable.S / (
                      obj.safety_parameters['Jmax'] * obj.safety_parameters['ku AuxiliaryInductor'])
    return res


def JLk(obj, X):
    res = obj.safety_parameters['Jmax'] - obj.calculated_values['TransformerIrms'] / (
                obj.auxiliary_inductor.Cable.Scu * obj.auxiliary_inductor.Ncond)
    return res


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

