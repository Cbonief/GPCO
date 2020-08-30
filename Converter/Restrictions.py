import numpy as np


# Entrance Inductor #
def dIin_max(obj, X, CalculatedValues):
    dIin = CalculatedValues['dIin']
    Iin = CalculatedValues['Iin']
    res = (obj.Features['dIin_max']*Iin - dIin)*100
    return res


def bmax_Li(obj, X, CalculatedValues):
    res = (obj.Features['Bmax']['EntranceInductor'] - CalculatedValues['BmaxLi'])
    return res


def AeAw_Li(obj, X, CalculatedValues):
    res = obj.EntranceInductor.Core.AeAw - CalculatedValues['LiIrms']*obj.EntranceInductor.Ncond*obj.EntranceInductor.Cable.S/(obj.Features['Jmax']*obj.SafetyParams['ku']['EntranceInductor'])
    return res


def JLi(obj, X, CalculatedValues):
    return (obj.Features['Jmax'] - CalculatedValues['LiIrms']/(obj.EntranceInductor.Cable.Scu*obj.EntranceInductor.Ncond))/1000000


# Auxiliary Inductor #
def bmax_Lk(obj, X, CalculatedValues):
    res = (obj.Features['Bmax']['AuxiliaryInductor'] - CalculatedValues['BmaxLk'])
    return res


def AeAw_Lk(obj, X, CalculatedValues):
    res = obj.AuxiliaryInductor.Core.AeAw - CalculatedValues['TransformerIrms'][0]*obj.EntranceInductor.Ncond*obj.AuxiliaryInductor.Cable.S/(obj.Features['Jmax']*obj.SafetyParams['ku']['AuxiliaryInductor'])
    return res


def JLk(obj, X, CalculatedValues):
    return obj.Features['Jmax'] - CalculatedValues['TransformerIrms'][0]/obj.AuxiliaryInductor.Cable.Scu

#TransformerRestrictions = [Transformer_Core_Loss, Transformer_Cable_Loss]
# EntranceInductorRestrictions = [dIin_max, pen_indutor_Li, bmax_Li, AeAw_Li, JLi]
EntranceInductorRestrictions = [dIin_max]
AuxiliaryInductorRestrictions = [bmax_Lk, AeAw_Lk, JLk]
#CapacitorRestrictions = [Capacitor1_Loss, Capacitor2_Loss, Capacitor3_Loss, Capacitor4_Loss]
#DiodeRestrictions = [Diode3_Loss, Diode4_Loss]
#SwitchRestrictions = [Switch1_Loss, Switch2_Loss]