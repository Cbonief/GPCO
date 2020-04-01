import numpy as np
from FileHandler import loadFSD
import Auxiliar_Functions as af

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
    def __init__(self, core, cable, N, Ncond):
        self.Core = core
        self.Cable = cable
        self.N = N
        self.Ncond = Ncond

        self.Dstr = cable.Dcu / np.sqrt(Ncond)
        self.FSD = FSD[Ncond - 1]
        self.NC = np.ceil(self.FSD * self.Cable.D * N / self.Core.Bj)
        self.Ncond = Ncond
        self.Ada = np.sqrt(1/Ncond) * self.Cable.D * self.NC / self.Core.Bj
        self.Penetration_base = np.sqrt(self.Cable.Rho / (np.pi * self.Cable.Ur * uo))
        self.A_base = np.power(np.pi / 4, 0.75) * self.Dstr * np.sqrt(self.Ada) / self.Penetration_base
        self.rca = []
        self.rcc = self.Cable.Rho * (self.Core.Lt + 8 * self.NC * self.Cable.D * self.FSD) * self.N / (
                    self.Ncond * self.Cable.Scu)

    def calculate_rca(self, fs, noc):
        for n in range(0, noc):
            if n == 0:
                ratio = 1
            else:
                a = self.A_base * np.sqrt(n*fs)
                # print('A', n, '= ', a)
                ratio = a*(af.f1(a) + (2/3)*(self.Ncond*self.NC**2 - 1)*af.f2(a))
            self.rca.append(ratio * self.rcc)
        # for n in range(0, noc):
        #     print('Rca', '= ', self.rca[n])
        # print('-----------------------------------------------------')
    def get_rca(self, n):
        return self.rca[n]

    def get_inductance(self, gap_width):
        return (self.N**2)*uo*self.Core.Ae/gap_width


class Transformer:
    def __init__(self, core, cables, N, Ncond):
        self.Core = core
        self.Primary = Inductor(core, cables[0], N[0], Ncond[0])
        self.Secondary = Inductor(core, cables[1], N[1], Ncond[1])
        self.Ratio = N[1]/N[0]


class Switch:
    def __init__(self, ton, toff, Rdson):
        self.Ton = ton
        self.Toff = toff
        self.Rdson = Rdson


class Diode:
    def __init__(self, vd, rt):
        self.Vd = vd
        self.Rt = rt


class Capacitor:
    def __init__(self, C, Rse):
        self.C = C
        self.RSE = Rse