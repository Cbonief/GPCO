import numpy as np
import math

def dIin_max(obj, X):
    dIin = obj.calculated_values['dIin']
    Iin = obj.calculated_values['Iin']
    res = (obj.design_features['dIin_max']*Iin - dIin)
    if math.isnan(res) or math.isinf(res):
        res = -1
    return res


def bmax_Li(obj, X):
    res = (obj.design_features['Bmax']['EntranceInductor'] - obj.calculated_values['BmaxLi'])
    return res


def AeAw_Li(obj, X):
    res = obj.entrance_inductor.Core.AeAw - obj.calculated_values['LiIrms']*obj.entrance_inductor.Ncond*obj.entrance_inductor.Cable.S/(obj.design_features['Jmax']*obj.SafetyParams['ku']['EntranceInductor'])
    return res


def JLi(obj, X):
    return (obj.design_features['Jmax'] - obj.calculated_values['LiIrms']/(obj.entrance_inductor.Cable.Scu*obj.entrance_inductor.Ncond))/1000000


# Auxiliary Inductor #
def bmax_Lk(obj, X):
    res = (obj.design_features['Bmax']['AuxiliaryInductor'] - obj.calculated_values['BmaxLk'])
    return res


def AeAw_Lk(obj, X):
    res = obj.auxiliary_inductor.Core.AeAw - obj.calculated_values['TransformerIrms'][0]*obj.entrance_inductor.Ncond*obj.auxiliary_inductor.Cable.S/(obj.design_features['Jmax']*obj.SafetyParams['ku']['AuxiliaryInductor'])
    return res


def JLk(obj, X):
    return obj.design_features['Jmax'] - obj.calculated_values['TransformerIrms'][0]/obj.auxiliary_inductor.Cable.Scu

#TransformerRestrictions = [Transformer_Core_Loss, Transformer_Cable_Loss]
# entrance_inductorRestrictions = [dIin_max, pen_indutor_Li, bmax_Li, AeAw_Li, JLi]
EntranceInductorRestrictions = [dIin_max]
AuxiliaryInductorRestrictions = [bmax_Lk, AeAw_Lk, JLk]
#CapacitorRestrictions = [Capacitor1_Loss, Capacitor2_Loss, Capacitor3_Loss, Capacitor4_Loss]
#DiodeRestrictions = [Diode3_Loss, Diode4_Loss]
#SwitchRestrictions = [Switch1_Loss, Switch2_Loss]

Restrictions = []
Restrictions.extend(EntranceInductorRestrictions)
# Restrictions.extend(AuxiliaryInductorRestrictions)


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