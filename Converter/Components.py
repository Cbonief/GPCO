import inspect

import numpy as np

uo = 4*np.pi*1e-7


def loadFSD():
    file = open("D:\Desktop\Boni\Code\Python\ConverterOptimizer\Converter\FSD\FSD_data.txt", "r")
    contents = file.readlines()
    file.close()
    fsd = []
    for line in contents:
        aux = line.split("\t")
        aux2 = aux[1].split("\n")
        fsd.append(float(aux2[0]))
    return tuple(fsd)

FSD = ()
try:
    FSD = loadFSD()
except FileNotFoundError:
    print('Didn´t find FSD')


# Classe base que contém o nome do componente.
class Component:
    type = 'Component'

    def __init__(self, Name):
        self.Name = Name

    def set_name(self, new_name):
        self.Name = new_name

    def get_name(self):
        return self.Name

    def __hash__(self):
        return self.Name

    def __repr__(self):
        representation = "\n{} {} \n".format(self.type, self.Name)
        for i in inspect.getmembers(self):
            if not i[0].startswith('_') and not i[0] == 'Name' and not i[0] == 'type':
                if not inspect.ismethod(i[1]):
                    representation += "{}: = {}\n".format(i[0], i[1])
        return representation


class Switch(Component):
    type = 'Switch'

    def __init__(self, ton, toff, Rdson, Vmax, Cds=0, Name=None):
        Component.__init__(self, Name)
        self.Ton = ton
        self.Toff = toff
        self.Rdson = Rdson
        self.Vmax = Vmax
        self.Cds = Cds


class Diode(Component):
    type = 'Diode'

    def __init__(self, vd, rt, Vmax, Name=None):
        Component.__init__(self, Name)
        self.Vd = vd
        self.Rt = rt
        self.Vmax = Vmax


class Capacitor(Component):
    type = 'Capacitor'

    def __init__(self, C, Rse, Vmax, Name=None):
        Component.__init__(self, Name)
        self.C = C
        self.RSE = Rse
        self.Vmax = Vmax    


class Cable(Component):
    type = 'Cable'

    def __init__(self, Dcu, D, rho, Ur, Name=None):
        Component.__init__(self, Name)
        self.Scu = np.pi*(Dcu**2)/4
        self.Dcu = Dcu
        self.S = np.pi*(D**2)/4
        self.D = D
        self.Rho = rho
        self.Ur = Ur


class Core(Component):
    type = 'Core'

    def __init__(self, AeAw, Ae, Aw, Ve, Kc, alpha, beta, lt, Bj, Name=None):
        Component.__init__(self, Name)
        self.AeAw = AeAw
        self.Ae = Ae
        self.Aw = Aw
        self.Ve = Ve
        self.Kc = Kc
        self.Alpha = alpha
        self.Beta = beta
        self.Lt = lt
        self.Bj = Bj


class Inductor(Component):
    def __init__(self, core, cable, N, Ncond, Name=None):
        Component.__init__(self, Name)
        self.Core = core
        self.Cable = cable
        self.N = N
        self.Ncond = Ncond
        self.Penetration_base = None
        self.NC = None
        self.FSD = None
        self.A_base = None
        self.rcc = None
        self.rca = None
        self.used_area = self.Cable.S * self.N * self.Ncond

    def calculate_rcc(self):
        self.Penetration_base = np.sqrt(self.Cable.Rho / (np.pi * self.Cable.Ur * uo))
        dsq = self.Cable.Dcu*np.sqrt(np.pi/self.Ncond)/2
        self.FSD = FSD[self.Ncond - 1]
        self.NC = np.ceil(self.FSD*self.Cable.D * self.N / self.Core.Bj)
        ada = (self.N/self.NC)*dsq/self.Core.Bj
        dn_base = self.Penetration_base/np.sqrt(ada)
        self.A_base = dsq/dn_base
        self.rcc = self.Cable.Rho * (self.Core.Lt + 8 * self.NC * self.Cable.D * self.FSD) * self.N / (
                    self.Ncond * self.Cable.Scu)

    # Calcula a RCA do conversor com a metodologia de Dowell. Utiliza um fo fundamental e um número 'noc' de termos
    # serão calculados.
    def calculate_rca(self, fo, noc):
        self.rca = np.zeros(noc)
        for n in range(0, noc):
            if n == 0:
                ratio = 1
            else:
                a = self.A_base * np.sqrt(n*fo)
                ratio = a*(f1(a) + (2/3)*((self.NC-1)**2)*f2(a))
            self.rca[n] = ratio * self.rcc

    def get_rca(self, n):
        return self.rca[n]

    def get_inductance(self, gap_width):
        return (self.N**2)*uo*self.Core.Ae/gap_width

    def is_feasible(self, ku):
        return self.Core.Aw * ku >= self.used_area

    def utilization_factor(self, ku):
        return self.used_area / (ku*self.Core.Aw)


class Transformer(Component):
    def __init__(self, core, cables, N, Ncond, Name=None):
        Component.__init__(self, Name)
        self.Core = core
        self.Primary = Inductor(core, cables[0], N[0], Ncond[0])
        self.Secondary = Inductor(core, cables[1], N[1], Ncond[1])
        self.Ratio = N[1]/N[0]
        self.used_area = self.Primary.used_area + self.Secondary.used_area

    def is_feasible(self, ku):
        return self.used_area / ku > self.Core.Aw

    def utilization_factor(self, ku):
        return self.used_area / (ku*self.Core.Aw)


# Funções auxiliares necessárias para calcular a RCA de um indutor.
def f1(delta):
    return (np.sinh(2*delta) + np.sin(2*delta))/(np.cosh(2*delta) - np.cos(2*delta))

def f2(delta):
    return (np.sinh(delta) - np.sin(delta))/(np.cosh(delta) + np.cos(delta))