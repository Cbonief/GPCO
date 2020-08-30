import numpy as np
from scipy.optimize import fsolve


def fvo(X, k1, k2, Vo):
    Vc3 = X[0]
    Vc4 = X[1]
    D = X[2]
    return [Vo ** 3 + k1 * (Vc3 ** 2) * (Vc4 - k2) * (Vc4 * (1 - D) + D * k2), Vo ** 3 + k1 * (Vc4 ** 2) * (Vc3 + k2) * (Vc3 * (1 - D) - D * k2), Vc3 + Vc4 - Vo]


def vc3_vc4_d(obj, fs, Lk):
    Ts = 1 / fs
    x0 = [obj.Features['Vo'] / 2, obj.Features['Vo'] / 2, 0.5]
    k1 = obj.Features['Ro'] * Ts / (2 * Lk * obj.Features['Vi']['Nominal'] * (obj.Transformer.Ratio ** 3))
    k2 = obj.Transformer.Ratio * obj.Features['Vi']['Nominal']
    sol = fsolve(fvo, x0, args=(k1, k2, obj.Features['Vo']))
    return sol


def VoDx(k1, k2, X, D=0.55):
    Vc3 = X[0]
    Vc4 = X[1]
    
    f1 = (Vc3 + Vc4) ** 3 + k1 * (Vc3 ** 2) * (Vc4 - k2) * (Vc4 * (1 - D) + D * k2) + 1 / (10*Vc3) + 1 / (10*Vc4) + 1/(1000*(Vc3 + Vc4))
    f2 = (Vc3 + Vc4) ** 3 + k1 * (Vc4 ** 2) * (Vc3 + k2) * (Vc3 * (1 - D) - D * k2) + 1 / (10*Vc3) + 1 / (10*Vc4) + 1/(1000*(Vc3 + Vc4))

    j11 = 3 * ((Vc3 + Vc4) ** 2) + 2 * k1 * Vc3 * (Vc4 - k2) * (Vc4 * (1 - D) + D * k2)
    j12 = 3 * ((Vc3 + Vc4) ** 2) + k1 * (Vc3 ** 2) * (2 * Vc4 * (1 - D) - 2 * D + 1)
    j21 = 3 * ((Vc3 + Vc4) ** 2) + k1 * (Vc4 ** 2) * (2 * Vc3 * (1 - D) + 2 * D - 1)
    j22 = 3 * ((Vc3 + Vc4) ** 2) + 2 * k1 * Vc4 * (Vc3 + k2) * (Vc3 * (1 - D) - D * k2)

    Djinv = j22 * j11 - j12 * j21
    Jinv = np.array([
        [j22 / Djinv, -j12 / Djinv]
        , [-j21 / Djinv, j11 / Djinv]
    ])
    F = np.array([f1, f2])
    dx = -np.matmul(Jinv, F)
    return dx

def Vc3Vc4(obj, fs, Lk):
    Ts = 1/fs
    X = np.array([obj.Features['Vo'] / 2, obj.Features['Vo'] / 2])
    error = 1
    k1 = obj.Features['Ro'] * Ts / (2 * Lk * obj.Features['Vi']['Nominal'] * (obj.Transformer.Ratio ** 3))
    k2 = obj.Transformer.Ratio * obj.Features['Vi']['Nominal']
    while error > 0.001:
        dx = VoDx(k1, k2, X)
        error = dx[0] ** 2 + dx[1] ** 2
        X = X + dx
    return X

def t3t6(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc3 = CalculatedValues['Vc3']
    Vc4 = CalculatedValues['Vc4']
    Vo = CalculatedValues['Vo']

    D = obj.Features['D']['Nominal']
    Vi = obj.Features['Vi']['Nominal']

    n = obj.Transformer.Ratio

    t3 = Ts * Vc4 * (Vc3 * (D - 1) + Vi * D * n) / (Vi * n * Vo)
    t6 = Ts * (Vi * (Vc4 * D + Vc3)*n + (D - 1) * Vc3 * Vc4) / (Vi * n * Vo)
    return [t3, t6]

def OutputVoltage(obj, fs, Lk, D):
    Ts = 1/fs
    X = np.array([obj.Features['Vo'] / 2, obj.Features['Vo'] / 2])
    error = 1
    k1 = obj.Features['Ro'] * Ts / (2 * Lk * obj.Features['Vi']['Nominal'] * (obj.Transformer.Ratio ** 3))
    k2 = obj.Transformer.Ratio * obj.Features['Vi']['Nominal']
    while error > 0.001:
        dx = VoDx(k1, k2, X, D)
        error = dx[0] ** 2 + dx[1] ** 2
        X = X + dx
    return X[0] + X[1]  # Retorna Vo, Vc3 e Vc4

def getD(obj, fs, Lk):
    x1 = 0.2
    x2 = 0.9
    fx1 = 400-OutputVoltage(obj, fs, Lk, x1)
    error = 1
    while error > 0.5:
        x3 = (x1+x2)/2
        fx3 = 400-OutputVoltage(obj, fs, Lk, x3)
        if np.sign(fx1) == np.sign(fx3):
            x1 = x3
            fx1 = fx3
        else:
            x2 = x3
        error = abs(fx3)
    return x3


def TransformerIRms(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc3 = CalculatedValues['Vc3']
    Vc4 = CalculatedValues['Vc4']
    t3 = CalculatedValues['t3']
    t6 = CalculatedValues['t6']
    Vc1 = CalculatedValues['Vc1']
    Vc2 = CalculatedValues['Vc2']
    Ipk_pos_1 = CalculatedValues['Ipk_pos_1']
    Ipk_neg_1 = CalculatedValues['Ipk_neg_1']


    D = obj.Features['D']['Nominal']
    n = obj.Transformer.Ratio
    Lk = CalculatedValues['Lk']

    Ip_rms = t3*Ipk_pos_1**2 - (t3**2)*Ipk_pos_1*((Vc2 + Vc3/n)/Lk) + ((t3**3)/3)*((Vc2 + Vc3/n)/Lk)**2
    Ip_rms = Ip_rms + (((D*Ts)**3)/3)*((Vc4/n - Vc2)/Lk)**2
    Ip_rms = Ip_rms + (t6-D*Ts)*Ipk_neg_1**2 + ((t6-D*Ts)**2)*((Vc4/n + Vc1)/Lk) + (((t6-D*Ts)**3)/3)*((Vc4/n + Vc1)/Lk)**2
    Ip_rms = Ip_rms + (((Ts-t6)**3)/3)*((Vc1 - Vc3/n)/Lk)**2
    Ip_rms = np.sqrt(Ip_rms/Ts)
    #print(Ip_rms)
    Is_rms = Ip_rms/n
    return [Ip_rms, Is_rms]


def AuxiliaryInductorVrms(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc3 = CalculatedValues['Vc3']
    Vc4 = CalculatedValues['Vc4']
    t3 = CalculatedValues['t3']
    t6 = CalculatedValues['t6']
    Vc1 = CalculatedValues['Vc1']
    Vc2 = CalculatedValues['Vc2']

    D = obj.Features['D']['Nominal']
    n = obj.Transformer.Ratio
    b = [0, 0, 0, 0]
    a = [- (Vc2 + Vc3 / n), (Vc4 / n - Vc2), (Vc4 / n + Vc1), (Vc1 - Vc3 / n)]
    tf = [t3, D * Ts, t6, Ts]
    ti = [0, t3, D * Ts, t6]
    return rms_piecewise_linear(a, b, ti, tf, Ts)


def TransformerCurrentHarmonics(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc3 = CalculatedValues['Vc3']
    Vc4 = CalculatedValues['Vc4']
    t3 = CalculatedValues['t3']
    t6 = CalculatedValues['t6']
    Vc1 = CalculatedValues['Vc1']
    Vc2 = CalculatedValues['Vc2']
    Ipk_pos_1 = CalculatedValues['Ipk_pos_1']
    Ipk_neg_1 = CalculatedValues['Ipk_neg_1']

    D = obj.Features['D']['Nominal']
    n = obj.Transformer.Ratio
    Lk = CalculatedValues['Lk']

    A = [Ipk_pos_1, 0, Ipk_neg_1, 0]
    B = [- (Vc2 + Vc3 / n) / Lk, (Vc4 / n - Vc2) / Lk, (Vc4 / n + Vc1) / Lk, (Vc1 - Vc3 / n) / Lk]
    Tf = [t3, D * Ts, t6, Ts]
    Ti = [0, t3, D*Ts, t6]


    Harmonics = fourier_piecewise_linear(A, B, Ti, Tf, 1/Ts, 40)
    return Harmonics


def LiIrms(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    dIin = CalculatedValues['dIin']
    Imax = CalculatedValues['Ipk']
    Imin = CalculatedValues['Imin']

    D = obj.Features['D']['Nominal']
    A = [Imin, Imax]
    B = [dIin, -dIin]
    Tf = [D*Ts, Ts]
    Ti = [0, D*Ts]

    harmonics = rms_piecewise_linear(A, B, Ti, Tf, Ts)
    return harmonics


def InputCurrentHarmonics(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    dIin = CalculatedValues['dIin']
    Imax = CalculatedValues['Ipk']
    Imin = CalculatedValues['Imin']

    D = obj.Features['D']['Nominal']
    A = [Imin, Imax]
    B = [dIin, -dIin]
    Tf = [D*Ts, Ts]
    Ti = [0, D*Ts]

    harmonics = fourier_piecewise_linear(A, B, Ti, Tf, 1 / Ts, 40)
    return harmonics


def c1_irms(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc3 = CalculatedValues['Vc3']
    Vc4 = CalculatedValues['Vc4']
    t6 = CalculatedValues['t6']
    Ipk_neg_1 = CalculatedValues['Ipk_neg_1']
    Ipk = CalculatedValues['Ipk']
    Li = CalculatedValues['Li']

    D = obj.Features['D']['Nominal']
    Vi = obj.Features['Vi']['Nominal']
    n = obj.Transformer.Ratio
    Lk = CalculatedValues['Lk']
    dt1 = t6 - D * Ts
    dt2 = Ts - t6
    Vterm1 = Vi * D / (1 - D)

    # Primeira parte do integral.
    Ic1_rms = dt1*(Ipk - Ipk_neg_1)**2 - (dt1**2)*(Ipk - Ipk_neg_1)*(Vterm1/Li + (Vc4/n + Vterm1)/Lk) + (dt1**3)*((Vterm1/Li + (Vc4/n + Vterm1)/Lk)**2)/3
    # Segunda parte da integral.
    Ic1_rms = Ic1_rms + dt2*Ipk**2 - (dt2**2)*Ipk*(Vterm1/Li + (Vterm1 - Vc3/n)/Lk) + (dt2**3)*((Vterm1/Li + (Vterm1 - Vc3/n)/Lk)**2)/3
    Ic1_rms = np.sqrt(Ic1_rms/Ts)
    return Ic1_rms


def c2_irms(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc1 = CalculatedValues['Vc1']
    Vc2 = CalculatedValues['Vc2']
    Vc3 = CalculatedValues['Vc3']
    Vc4 = CalculatedValues['Vc4']
    t3 = CalculatedValues['t3']
    t6 = CalculatedValues['t6']
    Ipk_pos_1 = CalculatedValues['Ipk_pos_1']
    Ipk = CalculatedValues['Ipk']
    Li = CalculatedValues['Li']

    D = obj.Features['D']['Nominal']
    Vi = obj.Features['Vi']['Nominal']
    n = obj.Transformer.Ratio
    Lk = CalculatedValues['Lk']
    dt2 = (D * Ts - t3)
    dt3 = t6 - D*Ts
    dt4 = Ts - t6

    term1 = (Vc3/n + Vc2)/Lk
    term2 = (Vc4/n - Vc2)/Lk
    term3 = (Vi - (Vc1 + Vc2))/Li

    # Primeira parte da integral.
    Ic2_rms = t3*(Ipk_pos_1**2) - (t3**2)*Ipk_pos_1*term1 + (t3**3)*(term1**2)/3
    Ic2_rms = Ic2_rms + (dt2**3)*(term2**2)/3
    Ic2_rms = Ic2_rms + (dt4+dt3)*Ipk**2 + Ipk*term3*(dt3**2 + dt4**2) + ((dt3**3 + dt4**3)/3)*term3**2
    Ic2_rms = np.sqrt(Ic2_rms/Ts)
    #print('Corrente Ic2 ' + str(Ic2_rms))
    return Ic2_rms


def s1_irms(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc3 = CalculatedValues['Vc3']
    Vc4 = CalculatedValues['Vc4']
    t6 = CalculatedValues['t6']
    Ipk_neg_1 = CalculatedValues['Ipk_neg_1']
    Ipk = CalculatedValues['Ipk']
    Li = CalculatedValues['Li']

    D = obj.Features['D']['Nominal']
    Vi = obj.Features['Vi']['Nominal']
    n = obj.Transformer.Ratio
    Lk = CalculatedValues['Lk']

    Vterm1 = Vi * D / (1 - D)
    Is1_rms = (t6-D*Ts)*(Ipk_neg_1-Ipk)**2 + ((t6-D*Ts)**2)*(Ipk_neg_1-Ipk)*((Vc4/n + Vterm1)/Lk + Vterm1/Li)
    Is1_rms = Is1_rms + ((t6-D*Ts)**3)*(((Vc4/n + Vterm1)/Lk + Vterm1/Li)**2)/3
    Is1_rms = Is1_rms + (Ts - t6)*(Ipk**2) - ((Ts - t6)**2)*Ipk*((Vterm1 - Vc3/n)/Lk + Vterm1/Li)
    Is1_rms = Is1_rms + ((Ts - t6)**3)*(((Vterm1 - Vc3/n)/Lk + Vterm1/Li)**2)/3
    Is1_rms = np.sqrt(Is1_rms/Ts)
    #print('Correte Is1 ' + str(Is1_rms))
    return Is1_rms


def s2_irms(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc3 = CalculatedValues['Vc3']
    Vc4 = CalculatedValues['Vc4']
    t3 = CalculatedValues['t3']
    Ipk_pos_1 = CalculatedValues['Ipk_pos_1']
    Imin = CalculatedValues['Imin']
    Li = CalculatedValues['Li']

    D = obj.Features['D']['Nominal']
    Vi = obj.Features['Vi']['Nominal']
    n = obj.Transformer.Ratio
    Lk = CalculatedValues['Lk']

    Is2_rms = t3*(Imin - Ipk_pos_1)**2 + (t3**2)*(Imin - Ipk_pos_1)*(Vi/Li + (Vi + Vc3/n)/Lk)
    Is2_rms = Is2_rms + ((t3**3)/3)*(Vi/Li + (Vi + Vc3/n)/Lk)**2
    Is2_rms = Is2_rms + (D*Ts - t3)*Imin**2 + ((D*Ts - t3)**2)*(Vi/Li - (Vc4/n - Vi)/Lk)
    Is2_rms = Is2_rms + (((D*Ts - t3)**3)/3)*(Vi/Li - (Vc4/n - Vi)/Lk)**2
    Is2_rms = np.sqrt(Is2_rms/Ts)
    #print('Correte Is2 ' + str(Is2_rms))
    return Is2_rms


def D3Iavg(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc3 = CalculatedValues['Vc3']
    t3 = CalculatedValues['t3']
    t6 = CalculatedValues['t6']
    Ipk_pos_1 = CalculatedValues['Ipk_pos_1']

    D = obj.Features['D']['Nominal']
    Vi = obj.Features['Vi']['Nominal']
    n = obj.Transformer.Ratio
    Lk = CalculatedValues['Lk']

    Id3_avg = t3*(Ipk_pos_1/n) - (t3**2)*(Vi + Vc3/n)/(2*n*Lk)
    Id3_avg = Id3_avg + (Vi*D/(1-D) - Vc3/n)*((Ts-t6)**2)/(2*n*Lk)
    Id3_avg = Id3_avg/Ts
    return Id3_avg


def D3Irms(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc3 = CalculatedValues['Vc3']
    t3 = CalculatedValues['t3']
    t6 = CalculatedValues['t6']
    Ipk_pos_1 = CalculatedValues['Ipk_pos_1']

    D = obj.Features['D']['Nominal']
    Vi = obj.Features['Vi']['Nominal']
    n = obj.Transformer.Ratio
    Lk = CalculatedValues['Lk']

    Id3_rms = t3*(Ipk_pos_1/n)**2 - ((t3/n)**2)*Ipk_pos_1*(Vi + Vc3/n)/Lk + (t3**3)*(((Vi + Vc3/n)/(n*Lk))**2)/3
    Id3_rms = Id3_rms + ((Ts-t6)**3)*(((Vi*D/(1-D) - Vc3/n)/(n*Lk))**2)/3
    Id3_rms = np.sqrt(Id3_rms/Ts)
    return Id3_rms


def D4Iavg(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc4 = CalculatedValues['Vc4']
    t3 = CalculatedValues['t3']
    t6 = CalculatedValues['t6']
    Ipk_neg_1 = CalculatedValues['Ipk_neg_1']

    D = obj.Features['D']['Nominal']
    Vi = obj.Features['Vi']['Nominal']
    n = obj.Transformer.Ratio
    Lk = CalculatedValues['Lk']

    Id4_avg = -(t6-D*Ts)*(Ipk_neg_1/n) - ((t6-D*Ts)**2)*(Vi*D/(1-D) + Vc4/n)/(2*n*Lk)
    Id4_avg = Id4_avg - (-Vi + Vc4/n)*((D*Ts-t3)**2)/(2*n*Lk)
    Id4_avg = Id4_avg/Ts
    return Id4_avg


def D4Irms(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc4 = CalculatedValues['Vc4']
    t3 = CalculatedValues['t3']
    t6 = CalculatedValues['t6']
    Ipk_neg_1 = CalculatedValues['Ipk_neg_1']

    D = obj.Features['D']['Nominal']
    Vi = obj.Features['Vi']['Nominal']
    n = obj.Transformer.Ratio
    Lk = CalculatedValues['Lk']

    Id4_rms = ((D*Ts-t3)**3)*(((Vc4/n - Vi)/(Lk*n))**2)/3 + (t6-D*Ts)*(Ipk_neg_1/n)**2
    Id4_rms = Id4_rms + (Ipk_neg_1/Lk)*(Vc4/n + Vi*D/(1-D))*((t6-D*Ts)/n)**2
    Id4_rms = Id4_rms + (((t6-D*Ts)**3)/3)*((Vc4/n + Vi*D/(1-D))/(n*Lk))**2
    Id4_rms = np.sqrt(Id4_rms/Ts)
    return Id4_rms


def C3Irms(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc3 = CalculatedValues['Vc3']
    t3 = CalculatedValues['t3']
    t6 = CalculatedValues['t6']
    Ipk_pos_1 = CalculatedValues['Ipk_pos_1']
    Io = CalculatedValues['Io']

    D = obj.Features['D']['Nominal']
    Vi = obj.Features['Vi']['Nominal']
    n = obj.Transformer.Ratio
    Lk = CalculatedValues['Lk']

    Ic3_rms = t3*(Ipk_pos_1/n - Io)**2 - (t3**2)*(Ipk_pos_1/n - Io)*((Vi + Vc3/n)/(n*Lk))
    Ic3_rms = Ic3_rms + (t3**3)*(((Vi + Vc3/n)/(n*Lk))**2)/3
    Ic3_rms = Ic3_rms + (Ts - t3)*Io**2 - (Io/(n*Lk))*(Vi*D/(1-D) - Vc3/n)*(Ts - t6)**2
    Ic3_rms = Ic3_rms + ((Ts-t6)**3)*(((Vi*D/(1-D) - Vc3/n)/(n*Lk))**2)/3
    Ic3_rms = np.sqrt(Ic3_rms/Ts)
    return Ic3_rms


def C4Irms(obj, CalculatedValues):
    Ts = CalculatedValues['Ts']
    Vc4 = CalculatedValues['Vc4']
    t3 = CalculatedValues['t3']
    t6 = CalculatedValues['t6']
    Ipk_neg_1 = CalculatedValues['Ipk_neg_1']
    Io = CalculatedValues['Io']

    D = obj.Features['D']['Nominal']
    Vi = obj.Features['Vi']['Nominal']
    n = obj.Transformer.Ratio
    Lk = CalculatedValues['Lk']

    Ic4_rms = (Ts*(1+D) - t6)*Io**2 + Io*((Vc4/n - Vi)/(n*Lk))*(D*Ts-t3)**2
    Ic4_rms = Ic4_rms + ((D*Ts-t3)**3)*(((Vc4/n - Vi)/(n*Lk))**2)/3
    Ic4_rms = Ic4_rms + (t6-D*Ts)*(Io + Ipk_neg_1/n)**2
    Ic4_rms = Ic4_rms + ((t6-D*Ts)**2)*(Io + Ipk_neg_1/n)*((Vc4/n + Vi*D/(1-D))/(n*Lk))
    Ic4_rms = Ic4_rms + ((t6-D*Ts)**3)*(((Vc4/n + Vi*D/(1-D))/(n*Lk))**2)/3
    Ic4_rms = np.sqrt(Ic4_rms/Ts)
    return Ic4_rms


def Fourier(time, function, fo, noc):
    harmonic_amplitudes = np.zeros(noc)
    tmax = time[-1]
    dt = time[2] - time[1]
    term_base = 2 * np.pi * fo
    for n in range(1, noc):
        an = 0
        bn = 0
        term = term_base * n
        for [t, f] in zip(time, function):
            term2 = term*t
            an += f*np.cos(term2)
            bn += f*np.sin(term2)
        cn = np.sqrt(an**2 + bn**2)*2*dt/tmax
        harmonic_amplitudes[n] = cn
    #print(harmonic_amplitudes)
    return harmonic_amplitudes


def fourier_piecewise_linear(A,B,Ti, Tf, fo, noc):
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


def rms_piecewise_linear(A, B, Ti, Tf, Ts):
    rms = 0
    for [a, b, ti, tf] in zip(A, B, Ti, Tf):
        rms += (tf - ti)*(a - b*ti)**2 + (tf**2 - ti**2)*(a-b*ti)*b + (tf**3 - ti**3)*(b**2)/3
    rms = np.sqrt(rms/Ts)
    return rms


def f1(delta):
    return (np.sinh(2*delta) + np.sin(2*delta))/(np.cosh(2*delta) - np.cos(2*delta))


def f2(delta):
    return (np.sinh(delta) - np.sin(delta))/(np.cosh(delta) + np.cos(delta))
