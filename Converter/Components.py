import numpy as np

uo = 4*np.pi*1e-7

FSD = (0, 1, 2, 2.17, 2.42, 2.57, 2.82, 3, 3.25, 3.45, 3.64, 3.81, 3.98, 4.15, 4.3, 4.45, 4.6, 4.75, 4.88, 5.01, 5.14,
       5.27, 5.39, 5.51, 5.63, 5.75, 5.86, 5.98, 6.09, 6.19, 6.3, 6.4, 6.51, 6.6, 6.71, 6.8, 6.9, 6.99, 7.09, 7.18,
       7.27, 7.36, 7.45, 7.54, 7.63, 7.71, 7.8, 7.88, 7.97, 8.05, 8.13, 8.21, 8.29, 8.37, 8.45, 8.53, 8.61, 8.68, 8.76,
       8.83, 8.91, 8.98, 9.06, 9.13, 9.2, 9.27, 9.34, 9.41, 9.48, 9.55, 9.62, 9.69, 9.76, 9.83, 9.89, 9.96, 10.03,
       10.09, 10.16, 10.22, 10.29, 10.35, 10.41, 10.48, 10.54, 10.6, 10.67, 10.73, 10.79, 10.85, 10.91, 10.97, 11.03,
       11.09, 11.15, 11.21, 11.27, 11.33, 11.38, 11.44, 11.5)


# Classe base que contém o nome do componente.
class Component:
    type = 'Base'

    def __init__(self, Name):
        self.Name = Name

    def set_name(self, new_name):
        self.Name = new_name

    def get_name(self):
        return self.Name

    def __hash__(self):
        return self.Name

    def __repr__(self):
        return "{}".format(self.Name)

    # def __repr__(self):
    #     representation = "\n{} {} \n".format(self.type, self.Name)
    #     for i in inspect.getmembers(self):
    #         if not i[0].startswith('_') and not i[0] == 'Name' and not i[0] == 'type':
    #             if not inspect.ismethod(i[1]):
    #                 representation += "{}: = {}\n".format(i[0], i[1])
    #     return representation


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
        self.FSD = FSD[self.Ncond]
        self.A_base = None
        self.rcc = None
        self.rca = None
        self.used_area = self.Cable.S * self.N * self.Ncond
        self.calculate_rcc()

    # Calculates the DC component of the inductor's resistance.
    def calculate_rcc(self):
        self.Penetration_base = np.sqrt(self.Cable.Rho / (np.pi * self.Cable.Ur * uo))
        dsq = self.Cable.Dcu * np.sqrt(np.pi / self.Ncond) / 2
        self.NC = np.ceil(self.FSD * self.Cable.D * self.N / self.Core.Bj)
        ada = (self.N / self.NC) * dsq / self.Core.Bj
        dn_base = self.Penetration_base / np.sqrt(ada)
        self.A_base = dsq / dn_base
        self.rcc = self.Cable.Rho * (self.Core.Lt + 8 * self.NC * self.Cable.D * self.FSD) * self.N / (
                self.Ncond * self.Cable.Scu)

    # Calculates 'n' components of the inductor's AC resistance, using the Dowell Method.
    def calculate_rca(self, f, n):
        self.rca = np.zeros(n)
        for i in range(0, n):
            if i == 0:
                ratio = 1
            else:
                a = self.A_base * np.sqrt(i * f)
                ratio = a * (f1(a) + (2 / 3) * ((self.NC - 1) ** 2) * f2(a))
            self.rca[i] = ratio * self.rcc

    def get_rca(self, n):
        return self.rca[n]

    def get_inductance(self, gap_width):
        return (self.N ** 2) * uo * self.Core.Ae / gap_width

    def is_feasible(self, ku):
        return self.Core.Aw * ku >= self.used_area

    def utilization_factor(self, ku):
        return self.used_area / (ku * self.Core.Aw)

    def get_dictionary(self):
        return {'Core': self.Core.Name, 'Cable': self.Cable.Name, 'N': self.N, 'Ncond': self.Ncond}


class Transformer(Component):
    def __init__(self, core, cables, N, Ncond, Name=None):
        Component.__init__(self, Name)
        self.Core = core
        self.Primary = Inductor(core, cables[0], N[0], Ncond[0])
        self.Secondary = Inductor(core, cables[1], N[1], Ncond[1])
        self.Ratio = N[1] / N[0]
        self.used_area = self.Primary.used_area + self.Secondary.used_area

    def is_feasible(self, ku):
        return self.Core.Aw * ku >= self.used_area

    def utilization_factor(self, ku):
        return self.used_area / (ku * self.Core.Aw)

    def get_dictionary(self):
        return {
            'Core': self.Core.Name,
            'Primary Cable': self.Primary.Cable.Name,
            'Secondary Cable': self.Secondary.Cable.Name,
            'Primary N': self.Primary.N,
            'Secondary N': self.Secondary.N,
            'Primary Ncond': self.Primary.Ncond,
            'Secondary Ncond': self.Secondary.Ncond
        }


# Funções auxiliares necessárias para calcular a RCA de um indutor.
def f1(delta):
    return (np.sinh(2 * delta) + np.sin(2 * delta)) / (np.cosh(2 * delta) - np.cos(2 * delta))


def f2(delta):
    return (np.sinh(delta) - np.sin(delta)) / (np.cosh(delta) + np.cos(delta))
