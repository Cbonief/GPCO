self.Dstr = cable.Dcu / np.sqrt(Ncond)
        self.FSD = FSD[Ncond - 1]
        self.NC = np.ceil(self.FSD*self.Cable.D * N / self.Core.Bj)
        self.Ada = np.sqrt(1/Ncond) * self.Cable.D * self.NC / self.Core.Bj
        self.A_base = np.power(np.pi / 4, 0.75) * self.Dstr * np.sqrt(self.Ada) / self.Penetration_base

        self.rcc = self.Cable.Rho * (self.Core.Lt + 8 * self.NC * self.Cable.D * self.FSD) * self.N / (
                    self.Ncond * self.Cable.Scu)