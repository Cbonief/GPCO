import numpy as np


def dIin_max(obj, X, CalculatedValues):
    """
      @type res: float
      """
    dIin = CalculatedValues['dIin']
    Iin = CalculatedValues['Iin']
    res = (0.1*Iin - dIin)*1e4
    return res


def pen_indutor(obj, X, CalculatedValues):
    """
      @type res: float
      """
    res = (2*obj.EntranceInductor.Penetration_base/np.sqrt(X[0]) - obj.EntranceInductor.Cable.Dcu)*1e6
    return res


def bmax_Li(obj, X, CalculatedValues):
    """
      @type res: float
      """
    res = (0.4 - CalculatedValues['BmaxLi'])*1e4
    return res


def bmax_Lk(obj, X, CalculatedValues):
    """
      @type res: float
      """
    res = (0.15 - CalculatedValues['BmaxLk'])*1e4
    return res