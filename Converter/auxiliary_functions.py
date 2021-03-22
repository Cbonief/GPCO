import datetime

from scipy.optimize import fsolve

from Converter.Restrictions import *
from Converter.fqs import *


# Calcula Vc3, Vc4 e a razão cíclica necessária para obter o valor de Vo desejado.
def vc3_vc4_d_simplified(obj, fs, Lk):
    Vi = obj.features['Vi']
    n = obj.transformer.Ratio
    Ro = obj.features['Ro']
    Vo = obj.features['Vo']
    k = 2 * fs * Lk * n ** 2 / Ro
    b = -obj.features['D_Expected'] - 1
    c = 2 * k + obj.features['D_Expected']
    d = -2 * k
    e = k

    D = -1
    dlist = single_quartic(1,b,c,d,e)
    found = False
    for dVal in dlist:
        if dVal.imag == 0:
            if 0.3 <= dVal.real <= 0.7:
                D = dVal.real
                found = True
    if not found:
        print("Gain Error at [{},{}]; [{},{}]".format(fs, Lk, gain_restriction(obj, [fs, 0, Lk]),
                                                      gain_restriction_2(obj, [fs, 0, Lk])))
        raise ValueError
    else:
        vc3 = n * (D * Vi / (1 - D) - 2 * n * Lk * fs * Vo / (Ro * D ** 2))
        vc4 = n * (Vi - 2 * n * Lk * fs * Vo / (Ro * (1 - D) ** 2))
        solution = [vc3, vc4, D]
    return solution


def Vo_ideal(obj, D):
    Vi = obj.features['Vi']
    n = obj.transformer.Ratio
    Ro = obj.features['Ro']

    return n * Vi / (1 - D)


def Vo_simplified(obj, D, fs, Lk):
    Vi = obj.features['Vi']
    n = obj.transformer.Ratio
    Ro = obj.features['Ro']

    return n * Vi * (D ** 2) * (1 - D) / (((2 * D - 1) ** 2 + 1) * (Lk * fs * n ** 2 / Ro) + (D * (1 - D)) ** 2)


def Vo(obj, D, fs, Lk):
    Vi = obj.features['Vi']
    n = obj.transformer.Ratio
    Ro = obj.features['Ro']
    k1 = 2 * Lk * fs * Vi * n ** 3 / Ro
    k2 = n * Vi

    VoIdeal = Vo_ideal(obj, D) / 2
    x0 = [VoIdeal, VoIdeal]

    solution = fsolve(fvc3vc4, x0, args=(k1, k2, D))
    return sum(solution)


# System of equations to solve for Vc3, Vc4 and D, in terms of Vo.
def fvo(X, k1, k2, Vo):
    Vc3 = X[0]
    Vc4 = X[1]
    D = X[2]
    return np.array([Vo + k1 * (Vc3 ** 2) * (Vc4 - k2) * (Vc4 * (1 - D) + D * k2) / (Vo ** 2),
                     Vo + k1 * (Vc4 ** 2) * (Vc3 + k2) * (Vc3 * (1 - D) - D * k2) / (Vo ** 2), Vc3 + Vc4 - Vo])


# System of equations to solve for Vc3, and Vc4, given D.
def fvc3vc4(X, k1, k2, D):
    Vc3 = X[0]
    Vc4 = X[1]
    return np.array([k1 * (Vc3 + Vc4) ** 3 + k1 * (Vc3 ** 2) * (Vc4 - k2) * (Vc4 * (1 - D) + D * k2),
                     k1 * (Vc3 + Vc4) ** 3 + (Vc4 ** 2) * (Vc3 + k2) * (Vc3 * (1 - D) - D * k2)])


'EQUAÇÕES DE TENSÃO E CORRENTE DOS COMPONENTES'


def TransformerIRms(obj, values):
    Ts = values['Ts']
    Vc3 = values['Vc3']
    Vc4 = values['Vc4']
    Vc1 = values['Vc1']
    Vc2 = values['Vc2']


    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']

    A = [0, 0]
    B = [(Vc4 / n - Vc2) / Lk, (Vc1 - Vc3 / n) / Lk]
    Tf = [D*Ts, Ts]
    Ti = [0, D*Ts]

    Ip_rms = rms_piecewise_linear(A, B, Ti, Tf, Ts)
    Is_rms = Ip_rms/n
    return [Ip_rms, Is_rms]


def AuxiliaryInductorVrms(obj, values):
    Ts = values['Ts']
    Vc3 = values['Vc3']
    Vc4 = values['Vc4']
    Vc1 = values['Vc1']
    Vc2 = values['Vc2']

    D = values['D']
    n = obj.transformer.Ratio

    A = [(Vc4 / n - Vc2), (Vc1 - Vc3 / n)]
    B = [0, 0]
    Tf = [D*Ts, Ts]
    Ti = [0, D*Ts]

    return rms_piecewise_linear(A, B, Ti, Tf, Ts)


def TransformerPrimaryCurrentHarmonics(obj, values):
    Ts = values['Ts']
    Vc3 = values['Vc3']
    Vc4 = values['Vc4']
    Vc1 = values['Vc1']
    Vc2 = values['Vc2']

    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']

    A = [0, 0]
    B = [(Vc4 / n - Vc2) / Lk, (Vc1 - Vc3 / n) / Lk]
    Tf = [D*Ts, Ts]
    Ti = [0, D*Ts]

    harmonics = fourier_piecewise_linear(A, B, Ti, Tf, 1/Ts, 40)
    return harmonics


def TransformerCurrentHarmonics(obj, values):
    Ts = values['Ts']
    Vc3 = values['Vc3']
    Vc4 = values['Vc4']
    Vc1 = values['Vc1']
    Vc2 = values['Vc2']

    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']

    A = [0, 0]
    B = [(Vc4 / n - Vc2) / Lk, (Vc1 - Vc3 / n) / Lk]
    Tf = [D*Ts, Ts]
    Ti = [0, D*Ts]

    harmonics = fourier_piecewise_linear(A, B, Ti, Tf, 1/Ts, 40)
    return harmonics

def LiIrms(obj, values):
    Ts = values['Ts']
    dIin = values['dIin']
    Imax = values['Ipk']
    Imin = values['Imin']

    D = values['D']
    A = [Imin, Imax]
    B = [dIin, -dIin]
    Tf = [D*Ts, Ts]
    Ti = [0, D*Ts]

    harmonics = rms_piecewise_linear(A, B, Ti, Tf, Ts)
    return harmonics


def InputCurrentHarmonics(obj, values):
    Ts = values['Ts']
    dIin = values['dIin']
    Imax = values['Ipk']
    Imin = values['Imin']

    D = values['D']
    A = [Imin, Imax]
    B = [dIin, -dIin]
    Tf = [D*Ts, Ts]
    Ti = [0, D*Ts]

    harmonics = fourier_piecewise_linear(A, B, Ti, Tf, 1 / Ts, 40)
    return harmonics


def c1_irms(obj, values):
    Ts = values['Ts']
    Vc1 = values['Vc1']
    Vc3 = values['Vc3']
    Iin = values['Iin']

    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']
    
    A = [0, Iin]
    B = [0, -(Vc1-Vc3/n)/Lk]
    Ti = [0, D*Ts]
    Tf = [D*Ts, Ts]
    return rms_piecewise_linear(A, B, Ti, Tf, Ts)


def c2_irms(obj, values):
    Ts = values['Ts']
    Vc2 = values['Vc2']
    Vc4 = values['Vc4']
    Iin = values['Iin']

    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']
    
    A = [0, Iin]
    B = [(Vc4/n - Vc2)/Lk, 0]
    Ti = [0, D*Ts]
    Tf = [D*Ts, Ts]

    return rms_piecewise_linear(A, B, Ti, Tf, Ts)


def s1_irms(obj, values):
    Ts = values['Ts']
    Vc1 = values['Vc1']
    Vc3 = values['Vc3']
    Iin = values['Iin']

    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']

    A = [0, -Iin]
    B = [0, (Vc1-Vc3/n)/Lk]
    Ti = [0, D*Ts]
    Tf = [D*Ts, Ts]

    return rms_piecewise_linear(A, B, Ti, Tf, Ts)


def s2_irms(obj, values):
    Ts = values['Ts']
    Vc2 = values['Vc2']
    Vc4 = values['Vc4']
    Iin = values['Iin']

    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']

    A = [Iin, 0]
    B = [-(Vc4/n - Vc2)/Lk, 0]
    Ti = [0, D*Ts]
    Tf = [D*Ts, Ts]

    oi = rms_piecewise_linear(A, B, Ti, Tf, Ts)
    return rms_piecewise_linear(A, B, Ti, Tf, Ts)


def D3Iavg(obj, values):
    Ts = values['Ts']
    Vc1 = values['Vc1']
    Vc3 = values['Vc3']

    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']

    A = [0, 0]
    B = [0, (Vc1-Vc3/n)/(n*Lk)]
    Ti = [0, D*Ts]
    Tf = [D*Ts, Ts]

    return avg_piecewise_linear(A, B, Ti, Tf, Ts)


def D3Irms(obj, values):
    Ts = values['Ts']
    Vc1 = values['Vc1']
    Vc3 = values['Vc3']

    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']

    A = [0, 0]
    B = [0, (Vc1-Vc3/n)/(n*Lk)]
    Ti = [0, D*Ts]
    Tf = [D*Ts, Ts]

    return rms_piecewise_linear(A, B, Ti, Tf, Ts)


def D4Iavg(obj, values):
    Ts = values['Ts']
    Vc2 = values['Vc2']
    Vc4 = values['Vc4']

    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']

    A = [0, 0]
    B = [-(Vc4/n-Vc2)/(n*Lk), 0]
    Ti = [0, D*Ts]
    Tf = [D*Ts, Ts]

    return avg_piecewise_linear(A, B, Ti, Tf, Ts)


def D4Irms(obj, values):
    Ts = values['Ts']
    Vc2 = values['Vc2']
    Vc4 = values['Vc4']

    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']

    A = [0, 0]
    B = [-(Vc4/n-Vc2)/(n*Lk), 0]
    Ti = [0, D*Ts]
    Tf = [D*Ts, Ts]

    return rms_piecewise_linear(A, B, Ti, Tf, Ts)


def C3Irms(obj, values):
    Ts = values['Ts']
    Vc1 = values['Vc1']
    Vc3 = values['Vc3']
    Io = values['Io']

    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']

    A = [-Io, -Io]
    B = [0, (Vc1-Vc3/n)/(n*Lk)]
    Ti = [0, D*Ts]
    Tf = [D*Ts, Ts]

    return rms_piecewise_linear(A, B, Ti, Tf, Ts)


def C4Irms(obj, values):
    Ts = values['Ts']
    Vc2 = values['Vc2']
    Vc4 = values['Vc4']
    Io = values['Io']

    D = values['D']
    n = obj.transformer.Ratio
    Lk = values['Lk']

    A = [-Io, -Io]
    B = [-(Vc4/n - Vc2)/(n*Lk), 0]
    Ti = [0, D*Ts]
    Tf = [D*Ts, Ts]

    return rms_piecewise_linear(A, B, Ti, Tf, Ts)

# Função que calcula a série de fourier de uma função consistente apenas de segmentos de reta.
def fourier_piecewise_linear(A, B, Ti, Tf, fo, noc):
    harmonic_amplitudes = np.zeros(noc)
    base = 2 * np.pi * fo
    for n in range(0, noc):
        term = base*n
        an = 0
        bn = 0
        if n == 0:
            for [a, b, ti, tf] in zip(A, B, Ti, Tf):
                an += (a-b*ti)*(tf-ti) + (b/2)*(tf**2 - ti**2)
            cn = an*fo
        else:
            for [a, b, ti, tf] in zip(A, B, Ti, Tf):
                costi = np.cos(term*ti)
                costf = np.cos(term*tf)
                sinti = np.sin(term*ti)
                sintf = np.sin(term*tf)
                an += ((sintf - sinti)*a + b*(tf-ti)*sintf + (b*(costf - costi)/term))/term
                bn += ((costi - costf)*a - b*(tf-ti)*costf + (b*(sintf - sinti)/term))/term
            cn = np.sqrt(an**2 + bn**2)*2*fo
        harmonic_amplitudes[n] = cn
    return harmonic_amplitudes

# Função que calcula o valor RMS de uma função consistente apenas de segmentos de reta.
def rms_piecewise_linear(A, B, Ti, Tf, Ts):
    rms = 0
    for [a, b, ti, tf] in zip(A, B, Ti, Tf):
        rms += (tf - ti)*(a - b*ti)**2 + (tf**2 - ti**2)*(a-b*ti)*b + (tf**3 - ti**3)*(b**2)/3
    rms = np.sqrt(rms/Ts)
    return rms

def avg_piecewise_linear(A, B, Ti, Tf, Ts):
    avg = 0
    for [a, b, ti, tf] in zip(A, B, Ti, Tf):
        avg += (tf - ti)*(a - b*ti) + (tf**2 - ti**2)*b/2
    avg = avg/Ts
    return avg


# def iZVS2(obj, f, Li):
#     Po = obj.design_features['Po']
#     Vo = obj.design_features['Vo']
#     Ro = obj.design_features['Ro']


#     return 2*obj.transformer.Ratio*Vo/(Ro*(1-Dmin)) - (Po/(2*Vmax)) + (Vmax*Dmin)/(2*Li_lower_bound*frequency_upper_bound)


'REMOVER DAQUI'
def rescale(vector, bounds, function=None):
    xmax = max(vector)
    xmin = min(vector)
    a = (bounds[1] - bounds[0]) / (xmax - xmin)
    b = (xmax * bounds[0] - xmin * bounds[1]) / (xmax - xmin)
    rescaled = np.zeros(np.size(vector))
    for index in range(0, np.size(vector)):
        rescaled[index] = a * vector[index] + b
        if function:
            rescaled[index] = function(rescaled[index])
    return rescaled