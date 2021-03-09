import math

from scipy.optimize import minimize

from Converter.auxiliary_functions import *
from GUI.Custom.FileHandler import loadFSD

Atr = [15.621321782051393, 0, -15.068631524735313, 0]
Btr = [-69308774.01484102, -1512163.845349491, 69424447.47128429, 1627837.3017927664]
Tftr = [2.2534511041495097e-07, 1.0188423339066433e-05, 1.0405433444793049e-05, 2e-05]
Titr = [0, 2.2534511041495097e-07, 1.0188423339066433e-05, 1.0405433444793049e-05]

A = [7.0977280680502846, 7.844800667581901]
B = [0.747072599531616, -0.747072599531616]
Tf = [1.1000000000000001e-05, 2e-05]
Ti = [0, 1.1000000000000001e-05]

print("Start")

HarmonicsTrafo = fourier_piecewise_linear(Atr, Btr, Titr, Tftr, 50e3, 40)

try:
    FSD = loadFSD()
except:
    print('Didn´t find FSD')

uo = 4*np.pi*1e-7


class Cable:
    def __init__(self, Dcu, D, rho, Ur):
        self.Scu = np.pi*(Dcu**2)/4
        self.Dcu = Dcu
        self.S = np.pi*(D**2)/4
        self.D = D
        self.Rho = rho
        self.Ur = Ur


class Core:
    def __init__(self, AeAw, Ae, Aw, Ve, Kc, alpha, beta, lt, Bj):
        self.AeAw = AeAw
        self.Ae = Ae
        self.Aw = Aw
        self.Ve = Ve
        self.Kc = Kc
        self.Alpha = alpha
        self.Beta = beta
        self.Lt = lt
        self.Bj = Bj


class Inductor:
    def __init__(self, core, cable, N, Ncond):
        self.Core = core
        self.Cable = cable
        self.N = N
        self.Ncond = Ncond

        self.Penetration_base = np.sqrt(self.Cable.Rho / (np.pi * self.Cable.Ur * uo))

        dsq = cable.Dcu *np.sqrt(np.pi/(4*Ncond))
        self.FSD = FSD[Ncond - 1]
        self.NC = np.ceil(self.FSD*self.Cable.D * N / self.Core.Bj)
        ada = (N/self.NC)*dsq/self.Core.Bj
        dn_base = self.Penetration_base/np.sqrt(ada)
        self.A_base = dsq/dn_base

        self.rca = []
        self.rcc = self.Cable.Rho*(self.Core.Lt + 8*self.NC*self.Cable.D*self.FSD)*self.N/(self.Ncond*self.Cable.Scu)

    def calculate_rca(self, fs, noc):
        for n in range(0, noc):
            if n == 0:
                ratio = 1
            else:
                a = self.A_base * np.sqrt(n*fs)
                ratio = a*(f1(a) + (2/3)*(self.Ncond*self.NC**2 - 1)*f2(a))
            self.rca.append(ratio * self.rcc)
    def get_rca(self, n):
        return self.rca[n]

    def get_inductance(self, gap_width):
        return (self.N**2)*uo*self.Core.Ae/gap_width


class Transformer:
    def __init__(self, core, cable, N, Ncond):
        self.Core = core
        self.Primary = Inductor(core, cable[0], N[0], Ncond[0])
        self.Secondary = Inductor(core, cable[1], N[1], Ncond[1])
        self.Ratio = N[1]/N[0]


def Transformer_Cable_Loss(Trafo):
    cable_loss_primary = 0
    cable_loss_secondary = 0

    for n in range(0, len(HarmonicsTrafo)):
        aux1 = 0.5
        aux2 = aux1
        if n == 0:
            aux1 = 1
            aux2 = 0
        cable_loss_primary += Trafo.Primary.get_rca(n)*(HarmonicsTrafo[n]**2)*aux1
        cable_loss_secondary += Trafo.Secondary.get_rca(n)*((HarmonicsTrafo[n]/Trafo.Ratio)**2)*aux2
    if math.isnan(cable_loss_primary):
        cable_loss_primary = 10
    return (cable_loss_primary - 0.718)**2

def InductorCableLoss(Inductor):
    cable_loss = 0
    for n in range(0, len(HarmonicsTrafo)):
        aux1 = 0.5
        if n == 0:
            aux1 = 1
        cable_loss += Inductor.get_rca(n)*(HarmonicsTrafo[n]**2)*aux1
    if math.isnan(cable_loss):
        cable_loss = 10
    return (0.235  - cable_loss)**2

N = [5, 59]
Ncond = [8, 1]
rho = 1.68e-8
AWG_23 = Cable(0.5753e-3, 0.5733e-3, rho, 0.999994)
Cables = [AWG_23, AWG_23]
NEE_20 = Core(0.08e-8, 0.312e-4, 0.26e-4, 1.34e-6, 7.9292e-3, 1.4017, 2.3294, 38e-3, 11.6e-3)
NEE_30_15 = Core(1.037e-8, 1.22e-4, 0.85e-4, 8.17e-6, 7.9292e-3, 1.4017, 2.3294, 13e-2, 0.09)


def objective(X):
    NEE_20.Lt = X[0]
    NEE_30_15.Lt = X[1]
    NEE_20.Bj = X[2]
    NEE_30_15.Bj = X[3]
    Lk = Inductor(NEE_20, AWG_23, 5, 8)
    Lk.calculate_rca(50e3, 40)
    Trafo = Transformer(NEE_30_15, Cables, N, Ncond)
    Trafo.Primary.calculate_rca(50e3, 40)
    Trafo.Secondary.calculate_rca(50e3, 40)
    return Transformer_Cable_Loss(Trafo)+InductorCableLoss(Lk)
#
x0 = [38e-3, 11.6e-3, 67e-3, 0.09]
b = (0, 1)
bound = ((1e-2, 10e-2), (1e-3, 10e-2),(1e-2, 10e-2), (1e-3, 10e-2))

def contraint(X):
    return [X[3] - X[1], X[2] - X[0]]

sol = minimize(
    objective,
    x0,
    method='COBYLA',
    bounds = bound,
    tol= 1e-15,
    options={'maxiter': 1000, 'disp': True,},
    constraints = {'fun': contraint, 'type': 'ineq'}
)
print(sol)