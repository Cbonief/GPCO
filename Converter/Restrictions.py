import numpy as np
import math

def dIin_max(obj, X):
    dIin = obj.calculated_values['dIin']
    Iin = obj.calculated_values['Iin']
    res = (obj.design_features['dIin_max']*Iin - dIin)
    return res


def bmax_Li(obj, X):
    res = (obj.design_features['Bmax']['EntranceInductor'] - obj.calculated_values['BmaxLi'])
    return res


def AeAw_Li(obj, X):
    res = obj.entrance_inductor.Core.AeAw - obj.calculated_values['LiIrms']*obj.entrance_inductor.Ncond*obj.entrance_inductor.Cable.S/(obj.design_features['Jmax']*obj.safety_params['ku']['EntranceInductor'])
    return res


def JLi(obj, X):
    res = obj.design_features['Jmax'] - obj.calculated_values['LiIrms']/(obj.entrance_inductor.Cable.Scu*obj.entrance_inductor.Ncond)
    return res


# Auxiliary Inductor #
def bmax_Lk(obj, X):
    res = (obj.design_features['Bmax']['AuxiliaryInductor'] - obj.calculated_values['BmaxLk'])
    return res


def AeAw_Lk(obj, X):
    res = obj.auxiliary_inductor.Core.AeAw - obj.calculated_values['TransformerIrms']*obj.entrance_inductor.Ncond*obj.auxiliary_inductor.Cable.S/(obj.design_features['Jmax']*obj.safety_params['ku']['AuxiliaryInductor'])
    return res


def JLk(obj, X):
    res = obj.design_features['Jmax'] - obj.calculated_values['TransformerIrms']/(obj.auxiliary_inductor.Cable.Scu*obj.auxiliary_inductor.Ncond)
    return res

def ZVS_restriction(converter, X):
    cs1 = converter.switches[0].Cds
    cs2 = converter.switches[1].Cds
    Po = converter.design_features['Po']
    Vo = converter.design_features['Vo']
    Vi = converter.design_features['Vi']['Nominal']
    Ro = converter.design_features['Ro']
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
    Po = converter.design_features['Po']
    Vo = converter.design_features['Vo']
    Ro = converter.design_features['Ro']
    n = converter.transformer.Ratio
    k1 = (cs1+cs2)*(Vi/(1-D))**2
    k2 = (2*n*Vo/D + 2*Po/Vi - Vi*D/(2*L*fs))**2

    return k1/k2

def Lk_restriction_s2(converter, Vi, D, L, fs):
    cs1 = converter.switches[0].Cds
    cs2 = cs1
    Po = converter.design_features['Po']
    Vo = converter.design_features['Vo']
    Ro = converter.design_features['Ro']
    n = converter.transformer.Ratio
    k1 = (cs1+cs2)*(Vi/(1-D))**2
    k2 = (2*n*Vo/(Ro*(1-D)) - Po/Vi + Vi*D/(2*L*fs))**2

    return k1/k2


def Gain_Restriction_Term(converter):
    Vo = converter.design_features['Vo']
    Ro = converter.design_features['Ro']
    n = converter.transformer.Ratio

    keys = ['Min', 'Max']
    Dbound = [converter.design_features['D']['Max']+0.01, converter.design_features['D']['Max']-0.01]

    term = 1e10
    for [D, key] in zip(Dbound, keys):
        Vi = converter.design_features['Vi'][key]
        new_term = Ro*D**2*(1-D)*(Vi*n - Vo*(1-D))/(Vo*((2*D-1)**2+1)*n**2)
        if new_term < term:
            term = new_term
    return term


def Gain_Restriction(converter, x):
    Po = converter.design_features['Po']
    Vo = converter.design_features['Vo']
    Vi = converter.design_features['Vi']['Nominal']
    n = converter.transformer.Ratio

    k1 = 1.16*n**2*Po
    nVi = n*Vi
    k2 = 0.0441*Vo
    LkFs = x[0]*x[2]
    return 100*(-LkFs + 0.8*Vo*(0.147*nVi-k2)/k1)

def Gain_Restriction_2(converter, x):
    Po = converter.design_features['Po']
    Vo = converter.design_features['Vo']
    Vi = converter.design_features['Vi']['Nominal']
    n = converter.transformer.Ratio

    k1 = 1.16*n**2*Po
    nVi = n*Vi
    k2 = 0.0441*Vo
    LkFs = x[0]*x[2]
    return 100*(LkFs - 1.2*Vo*(0.063*nVi-k2)/k1)

def LowerFsLk(converter):
    Po = converter.design_features['Po']
    Vo = converter.design_features['Vo']
    Vi = converter.design_features['Vi']['Nominal']
    n = converter.transformer.Ratio

    k1 = 1.16*n**2*Po
    nVi = n*Vi
    k2 = 0.0441*Vo
    return 1.2*Vo*(0.063*nVi-k2)/k1

def UpperFsLk(converter):
    Po = converter.design_features['Po']
    Vo = converter.design_features['Vo']
    Vi = converter.design_features['Vi']['Nominal']
    n = converter.transformer.Ratio

    k1 = 1.16*n**2*Po
    nVi = n*Vi
    k2 = 0.0441*Vo
    return 0.8*Vo*(0.147*nVi-k2)/k1

def Gain_Restriction_Feasible(converter, x):
    if Gain_Restriction(converter, x) > 0 and Gain_Restriction_2(converter, x) > 0:
        return True

EntranceInductorRestrictions = [dIin_max, bmax_Li, AeAw_Li]
AuxiliaryInductorRestrictions = [bmax_Lk, AeAw_Lk, JLk, ZVS_restriction]
#CapacitorRestrictions = [Capacitor1_Loss, Capacitor2_Loss, Capacitor3_Loss, Capacitor4_Loss]
#DiodeRestrictions = [Diode3_Loss, Diode4_Loss]
#SwitchRestrictions = [Switch1_Loss, Switch2_Loss]

Restrictions = []
Restrictions.extend(EntranceInductorRestrictions)
Restrictions.extend(AuxiliaryInductorRestrictions)
Restrictions.append(Gain_Restriction)
Restrictions.append(Gain_Restriction_2)

