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

        self.Penetration_base = np.sqrt(self.Cable.Rho / (np.pi * self.Cable.Ur * uo))

        dsq = cable.Dcu*np.sqrt(np.pi/Ncond)/2
        self.FSD = FSD[Ncond - 1]
        self.NC = np.ceil(self.FSD*self.Cable.D * N / self.Core.Bj)
        ada = (N/self.NC)*dsq/self.Core.Bj
        dn_base = self.Penetration_base/np.sqrt(ada)
        self.A_base = dsq/dn_base
        self.rcc = self.Cable.Rho * (self.Core.Lt + 8 * self.NC * self.Cable.D * self.FSD) * self.N / (
                    self.Ncond * self.Cable.Scu)
        
        self.rca = None

        self.used_area = cable.S * N * Ncond

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

    def recalculate_winding(self, ku, circuit_features=None):
        resolved = False
        while not resolved:
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
                self.set_parameter('Ncondp', ncond[0])
                self.set_parameter('Nconds', ncond[1])

    def set_parameter(self, name, value, ku=None):
        if name == 'Np':
            self.Primary.set_parameter('N', value)
        elif name == 'Ns':
            self.Secondary.set_parameter('Ncond', value)
        elif name == 'Ncondp':
            self.Primary.set_parameter('N', value)
        elif name == 'Nconds':
            self.Secondary.set_parameter('Ncond', value)

        self.used_area = self.Primary.used_area + self.Secondary.used_area
        if ku:
            if not self.is_feasible(ku):
                if name == 'Np':
                    self.set_parameter(name, (self.Core.Aw*ku - self.Secondary.used_area)/(self.Primary.Ncond*self.Primary.Cable.S))
                elif name == 'Ns':
                    self.set_parameter(name, (self.Core.Aw*ku - self.Primary.used_area)/(self.Secondary.Ncond*self.Secondary.Cable.S))
                elif name == 'Ncondp':
                    self.set_parameter(name, (self.Core.Aw*ku - self.Secondary.used_area)/(self.Primary.N*self.Primary.Cable.S))
                elif name == 'Nconds':
                    self.set_parameter(name, (self.Core.Aw * ku - self.Primary.used_area) / (self.Secondary.N * self.Secondary.Cable.S))



# Funções auxiliares necessárias para calcular a RCA de um indutor.
def f1(delta):
    return (np.sinh(2*delta) + np.sin(2*delta))/(np.cosh(2*delta) - np.cos(2*delta))

def f2(delta):
    return (np.sinh(delta) - np.sin(delta))/(np.cosh(delta) + np.cos(delta))