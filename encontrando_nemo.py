from Auxiliar_Functions import *
from FileHandler import loadFSD
from scipy.optimize import minimize

Atr =  [16.238567010594156, 0, -13.521694551413706, 0]
Btr =  [-36628359.21277461, -1388734.9770226472, 37277931.689644024, 2038307.4538920596]
Tftr =  [4.790240641923756e-07, 1.1000000000000001e-05, 1.1391943614149835e-05, 2e-05]
Titr =  [0, 4.790240641923756e-07, 1.1000000000000001e-05, 1.1391943614149835e-05]

A =  [7.0977280680502846, 7.844800667581901]
print((A[0]+A[1])/2)
B =  [0.747072599531616, -0.747072599531616]
Tf =  [1.1000000000000001e-05, 2e-05]
Ti =  [0, 1.1000000000000001e-05]

try:
    FSD = loadFSD()
except:
    print('Didn´t find FSD')
uo = 4*np.pi*1e-4


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
    def __init__(self, core, cable, N, Ncond, L):
        self.Core = core
        self.Cable = cable
        self.N = N
        self.Ncond = Ncond

        self.Dstr = cable.Dcu/np.sqrt(Ncond)
        self.FSD = FSD[Ncond - 1]
        self.NC = np.ceil(self.FSD * self.Cable.D * N / self.Core.Bj)
        self.width = self.FSD * self.Cable.D * N
        self.Ncond = Ncond
        self.Ada = np.sqrt(1/Ncond) * self.Cable.D * self.NC/self.Core.Bj
        self.Penetration_base = np.sqrt(self.Cable.Rho / (np.pi * self.Cable.Ur * uo))
        self.A_base = np.power(np.pi/4, 0.75) * self.Dstr * np.sqrt(self.Ada) / self.Penetration_base
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
    def __init__(self, core, cable, N, Ncond, L1, L2):
        self.Core = core
        self.Primary = Inductor(core, cable[0], N[0], Ncond[0], L1)
        self.Secondary = Inductor(core, cable[1], N[1], Ncond[1], L2)
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

    return (cable_loss_primary - 0.718)**2 + (cable_loss_secondary - 0.82)**2

def InductorCableLoss(Inductor):
    cable_loss = 0
    for n in range(0, len(HarmonicsTrafo)):
        aux1 = 0.5
        if n == 0:
            aux1 = 1
        cable_loss += Inductor.get_rca(n)*(HarmonicsTrafo[n]**2)*aux1
    return (0.235  - cable_loss)**2

N = [5, 59]
Ncond = [8, 1]
Cables = [AWG_23, AWG_23]

def objective(X):
    NEE_20 = Core(0.08e-8, 0.312e-4, 0.26e-4, 1.34e-6, 7.9292e-3, 1.4017, 2.3294, X[0], X[1])
    Lk = Inductor(NEE_20, AWG_23, 5, 8, np.sqrt(1/8))
    Lk.calculate_rca(50e3, 40)
    return InductorCableLoss(Lk)
#
x0 = [3.8e-2, 11.6e-3]
b = (0, 1)
bound = ((0, 3.8e-2+1e-4), b)


sol = minimize(objective, x0, method='SLSQP', bounds=bound, tol= 1e-15)
print(sol)