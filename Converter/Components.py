import numpy as np
from Converter import auxiliary_functions as af

uo = 4*np.pi*1e-4


def loadFSD():
    file = open("FSD/FSD_data.txt", "r")
    contents = file.readlines()
    file.close()
    fsd = []
    for line in contents:
        aux = line.split("\t")
        aux2 = aux[1].split("\n")
        fsd.append(float(aux2[0]))
    return tuple(fsd)


try:
    FSD = loadFSD()
except FileNotFoundError:
    print('Didn´t find FSD')


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
        self.rca = None
        self.rcc = self.Cable.Rho * (self.Core.Lt + 8 * self.NC * self.Cable.D * self.FSD) * self.N / (
                    self.Ncond * self.Cable.Scu)
        self.used_area = cable.S * N * Ncond

    def calculate_rca(self, fo, noc):
        self.rca = np.zeros(noc)
        for n in range(0, noc):
            if n == 0:
                ratio = 1
            else:
                a = self.A_base * np.sqrt(n*fo)
                ratio = a*(af.f1(a) + (2/3)*(self.Ncond*self.NC**2 - 1)*af.f2(a))
            self.rca[n] = ratio * self.rcc

    def get_rca(self, n):
        return self.rca[n]

    def get_inductance(self, gap_width):
        return (self.N**2)*uo*self.Core.Ae/gap_width

    def is_feasible(self, ku):
        return self.used_area / ku >= self.Core.Aw

    def recalculate_winding(self, ku):
        resolved = False
        n = 0
        ncond = 0
        while not resolved:
            n = np.random.randint(1, 200)
            ncond = np.random.randint(1, 50)
            inductor = Inductor(self.Core, self.Cable, n, ncond)
            resolved = inductor.is_feasible(ku)
        self.N = n
        self.Ncond = ncond

    def set_parameter(self, name, value, ku=None):
        if name == 'N':
            self.N = value
        elif name == 'Ncond':
            self.Ncond = value

        self.used_area = self.Cable.S * self.N * self.Ncond
        if ku:
            if not self.is_feasible(ku):
                if name == 'N':
                    self.set_parameter(name, self.Core.Aw*ku/(self.Ncond*self.Cable.S))
                elif name == 'Ncond':
                    self.set_parameter(name, self.Core.Aw*ku/(self.N*self.Cable.S))


class Transformer:
    def __init__(self, core, cables, N, Ncond):
        self.Core = core
        self.Primary = Inductor(core, cables[0], N[0], Ncond[0])
        self.Secondary = Inductor(core, cables[1], N[1], Ncond[1])
        self.Ratio = N[1]/N[0]
        self.used_area = self.Primary.used_area + self.Secondary.used_area

    def is_feasible(self, ku):
        return self.used_area / ku > self.Core.Aw

    def recalculate_winding(self, ku, circuit_features=None):
        resolved = False
        while not resolved:
            n = [0, 0]
            n = [np.random.randint(1, 200), np.random.randint(1, 200)]
            if circuit_features:
                while not found:
                    n = [np.random.randint(1, 200), np.random.randint(1, 200)]
                    a = circuit_features['Vi']['Nominal'] >= circuit_features['Vo']
                    b = n[0] >= n[1]
                    found = (a and b) or (not a and not b)
            ncond = [np.random.randint(1, 50), np.random.randint(1, 50)]
            transformer = Transformer(self.Core, [self.Primary.Cable, self.Secondary.Cable], n, ncond)
            resolved = transformer.is_feasible(ku)
            if resolved:
                self.set_parameter('Np', n[0])
                self.set_parameter('Ns', n[1])
                self.set_parameter('Npp', ncond[0])
                self.set_parameter('Nps', ncond[1])

    def set_parameter(self, name, value, ku=None):
        if name == 'Np':
            self.Primary.set_parameter('N', value)
        elif name == 'Ns':
            self.Secondary.set_parameter('Ncond', value)
        elif name == 'Npp':
            self.Primary.set_parameter('N', value)
        elif name == 'Nps':
            self.Secondary.set_parameter('Ncond', value)

        self.used_area = self.Primary.used_area + self.Secondary.used_area
        if ku:
            if not self.is_feasible(ku):
                if name == 'Np':
                    self.set_parameter(name, (self.Core.Aw*ku - self.Secondary.used_area)/(self.Primary.Ncond*self.Primary.Cable.S))
                elif name == 'Ns':
                    self.set_parameter(name, (self.Core.Aw*ku - self.Primary.used_area)/(self.Secondary.Ncond*self.Secondary.Cable.S))
                elif name == 'Npp':
                    self.set_parameter(name, (self.Core.Aw*ku - self.Secondary.used_area)/(self.Primary.N*self.Primary.Cable.S))
                elif name == 'Nps':
                    self.set_parameter(name, (self.Core.Aw * ku - self.Primary.used_area) / (self.Secondary.N * self.Secondary.Cable.S))


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
