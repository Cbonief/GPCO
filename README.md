Leia em [Português-BR](README-pt_BR.md)

# GPCO - General Power Converter Optimizer
Written by **Carlos Bonifácio Eberhardt Franco**

GPCO is a python based efficiency optimizer for switched-mode power converters that is able to optimize both the operating frequency and the components used, while satisfying the design constraints. It does this by separating the discrete and continuous variables into two layers of optimization.
The superficial layer uses a genetic algorithm to handle the discrete variables, while the second layer uses a numeric, gradient based algorithm to optimize the continuous variables.

* Obs: Up until this point, the only power converter available is the Boost Half Bridge DC-DC converter (Figure 1). However, the code is being generalized to easily accept other converters in the near future.

*Figure 1 - Boost Half Bridge DC-DC Converter*

![Hello](https://github.com/Cbonief/GPCO/blob/master/Imgs/BoostHalfBridgeConverter.png)

## Table of Contents
  - [1. Description of the Problem](#1-description-of-the-problem)
  - [2. Main Algorithm](#2-main-algorithm)
  	- [2.1 Genetic Algorithm](#21-genetic-algorithm)
  	- [2.2 Numeric Algorithm](#22-numeric-algorithm)
  - [3. Converter Implementation](#2-converter-implementation)
  	- [3.1 Components](#31-components)
  	- [3.2 The Model](#32-the-model)
	- [3.3 Losses](#33-losses)
	- [3.4 Restrictions](#34-restrictions)
  - [4. Future Work](#4-future-work)


## 1. Description of the Problem
The problem of optimizing a converter's characteristic while satisfying design and physical constraints can be mathematically write as:

![Optimization Problem](https://i.imgur.com/X1LOx7i.png)

Where X are all the converter's parameters that are considered free in the optimization, R are the performance requirements, such as: <img src="https://render.githubusercontent.com/render/math?math=V_i">, <img src="https://render.githubusercontent.com/render/math?math=V_o">, <img src="https://render.githubusercontent.com/render/math?math=\Delta_o">, etc. And finally K are component related restrictions and parameters, such as the maximum reverse voltage on a diode.

In the GPCO,  <img src="https://render.githubusercontent.com/render/math?math=\small F(X,R,K)"> is the efficiency of the converter, X are all components, switching frequency and inductance values. Some parameters, such as the value of the capacitances are not in X because the whole capacitor already is, and that include it's capacitance.

And <img src="https://render.githubusercontent.com/render/math?math=\small H(X,R,K)"> are all the restrictions of the converter, which include the maximum variation of the output voltage, the maximum magnetic induction permitted on the core of any inductor and many others.

## 2. Main Algorithm

### 2.1 Genetic Optimizer
As mentioned, the first layer of the algorithm is a simple GA (Genetic Algorithm), such as the one on the Figure 2, where the fitness of each individual is it's efficiency. The variables being optimized by this layer are the discrete components of the power converter: switches, diodes, capacitors and even the cores and cables of any inductor or transformer present on the circuit. Also included in this layer are the number of windings and parallel conductors on the inductors/transformers, both being considered to be integer only. 

*Figure 2 - Genetic Algorithm Flow Chart.*

![enter image description here](https://i.imgur.com/gPqnEkX.jpg)


## 2.2 Numeric Algorithm
The step "Test Population" is when the gradient based algorithm get's used, because the fitness that get's passed to the GA is actually the best efficiency possible for that set of discrete variables. This is the second layer of optimization, based on the continuous variables of the converter, which are: switching frequency and the value of the inductances.

In the GPCO the default numeric optimizer for this layer is SLSQP (Sequential Least Square Quadratic Programming), using the package SciPy. But in fact any optimizer that is able to deal with inequality constraints is suitable for the job. Some examples of these type of optimizers are: COBYLA, SUMT and ALAG.

## 3. Converter Implementation 

*A class diagram will be added soon.*

### 3.1 The Components
The latest implementation of the converter's components can be seen in the class diagram below. In it we see that all components inherit from the class Component, whose only information is the name of the component.

*Figure 3 -  Components Class Diagram*

![enter image description here](https://i.imgur.com/48baHHL.jpg)

### 3.2 The Model


### 3.3 Losses

### 3.4 Restrictions


## 4. Future work

The final goal for the GPCO is to be a generalized, multi topology, power converter optimizer. For that goal to happen, there a couple of milestones to be reached first:
- Refactor how the components are store in the converter:
Right now, all components are a separate variable inside the Boost Half Bridge class. That won't work if we want to have a wide arrange of converters, and even custom ones.
Most likely the components will have to be stored in a map inside the (not implemented yet) Converter class.
- Refactor the simulation, again:
Make a map between components and their simulation functions.
- Implement component especific restrictitions and losses in each component's class:
This goes hand in hand with the previous item.

## REFERENCES

AUDE. H. T. R; Notes on Quartic Curves. The American Mathematical Monthly. v. 56, n. 3, p. 165-170. 1949.

BALACHANDRAN, Swaminathan; LEE, Fred C.Y. Algorithms for Power Converter Design Optimization. IEEE Transactions on Aerospace and Electronic Systems. v. 17, n. 3. 1981.

BARBI, Ivo; MARTINS, Denizar Cruz. Introdução ao Estudos de Conversores c.c.-c.a.. 1°Ed. Florianópolis: Edição do Autor, 2005. v. 500. 489p.

BARBI, Ivo. Projeto de Fontes Chaveadas. 3ªEd. Florianópolis: Edição do Autor, 2014.

CARVALHO, Leticia Pivetta. Sistema de Projetos Otimizados de Conversores Estáticos (Poce) Usando Algoritmos Genéticos. Tese de Doutorado, UFSM. Santa Maria, RS; 2017.

CARDOSO, Nilton Pedro. Inversor Monofásico com Estágio c.c.-c.c. Boost Half Bridge Alimentado a partir de Bateria Veicular. Trabalho de Conclusão de Curso, UDESC. Joinville, SC; 2017.

CHINNECK, John W. Practical Optimization: A Gentle Introduction. Ottawa, Canada. Edição do Autor. Última edição em 2018.

DEMONTI, R; MARTINS, D. C.. Photovoltaic Energy Processing for Utility Connected System. Anais do VI Congresso Brasileiro de Eletrônica de Potência (COBEP 2001). Florianópolis, Brasil, pp. 735-739. 2001.

DURO, B; RAMDSEN, V. S; MUTTIK P. Minimization of active filter rating in high power hybrid filter systems. Anais da IEEE International Conference on Power Electronics Drive Systems. Hong Kong, Hong Kong, pp. 1043–1048. 1999.

ELWAKEIL, Ossama A.; ARORA, Jasbir S.;. Methods for Finding Feasbile Points in Constrained Optimization. AIAA Journal. v. 33 n. 9. 1995.

FIACCO, A.V; MCCORMICK, G.P. Nonlinear Programming: Sequential Unconstrained Minimization Techniques. New York. Editora Wiley, 1968.

FREUND, Robert. M. Penalty and Barrier Methods for Constrained Optimization. Massachusetts Institute of Technology. Edição do Autor, 2004.

HAUPT, R. L.; HAUPT, S. E. Practical Genetic Algorithms. Edição: 2nd. Hoboken, N.J: Wiley-Blackwell, 2004. ISBN 978-0-471-45565-3.

HESTENES, Magnus R.. Survey Paper: Multiplier and Gradient Methods. Journal of Optimization Theory and Applications. v. 4. n. 5. 1969.

JEENA, John. Implementation of a Novel Transformerless Inverter Topology for PV Application. International Journal of Latest Trends in Engineering and Technology. v. 8, n. 2, p. 301-306.

JIANG, Shuai; CAO, Dong; et. al. Grid-Connected Boost-Half-Bridge Photovoltaic Micro Inverter System Using Repetitive Current Control and Maximum Power Point Tracking. Twenty-Seventh Annual IEEE Applied Power Electronics Conference and Exposition (APEC). 2012.

KNAESEL, Carolina. Conversão c.c.-c.c. Isolado de Alto Ganho para Integração em Módulos Fotovoltaicos. Dissertação de Mestrado, UDESC. Joinville, SC; 2018.

MEJBRI, Hanen; AMMOUS, Kaiçar; et al. Bi-objective sizing optimization of power converter using genetic algorithms: Application to photovoltaic systems. COMPEL - The international journal for computation and mathematics in electrical and electronic engineering. v. 33, n. 1/2. 2014.

MONGE, Sergio B; et. al. Power Converter Design Optimization: a GA-based design approach to optimization of power electronics. IEEE Industry Applications Magazine. 2004.

MOTA, Paulo Vitor de Sousa. Desenvolvimento de um Inversor para Aplicações Fotovoltaicas com MPPT Integrado. Tese de Mestrado, Universidade do Minho. Braga; 2013.

PyQt – Python binding for Trolltech’s Qt applications Framework. Disponível em: <https://riverbankcomputing.com/pyqt/index.php>

POWELL, Michael James David. Direct Search Algorithms for Optimizations Calculations. Universidade de Cambridge, Departamento de Matemática Aplicada e Física Teórica. Cambridge; 1998.

POWELL, Michael James David. A view of algorithms for Optimization without derivatives. Universidade de Cambridge, Departamento de Matemática Aplicada e Física Teórica. Cambridge; 2007.

OLIVEIRA, Sérgio Vidal Garcia de. Otimização de Projeto de Fontes de Alimentação para Centrais de Telecomunicações. Dissertação de Mestrado, UFSC. Florianópolis, SC; 2001

RARDIN, Ronald. L. Optimization in Operations Research. 1ª Edição. Prentice Hall; New Jersey. 1998.

RIDLEY, Raymond. B; ZHOU, Chen; LEE, Fred. C. Application of Nonlinear Design Optimization Tool for Power Converter Components. IEEE Transactions on Power Electronics. v. 5, n. 1. 1990

RAHMAN, S; LEE, Fred. C. Nonlinear Program Based Optimization of Boost and Buck-Boost Converter Designs. 32nd International Spring Seminar on Electronics Technology. v. 32, n. 3, p. 257-281.

TEIXEIRA, Estêvão Coelho; BRAGA, Henrique Antônio Carvalho; et. al. Uma visão topológica sobre sistemas fotovoltaicos monofásicos conectados à rede de energia elétrica. Juiz de Fora. 2003

TIGGEMANN, Henrique. Análise e desenvolvimento de um inversor monofásico de baixa potência aplicado a sistemas de transporte. Trabalho de Conclusão de Curso, UNIVANTES. Lajeado, RS; 2008.

VIRTANEN Pauli, et al. e Contribuidores do SciPy 1.0. SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python. Nature Methods, v. 17, n. 3, p. 261-272. 2020. 

WODJA, Rafal P. Winding Resistance and Winding Power Loss of High-Frequency Power Inductors. Dissertação de PhD, Universidade Estadual de Wright, Ohio. 2012.

XUE, Yaosuo; CHANG, Liuchen; KÆR, Søren Bækhøj; et al. Topologies of Single-Phase Inverters for SmallDistributed Power Generators: An Overview. IEEE Transactions on Power Electronics. v. 19, n. 5. 2004.

YORK, Ben; YU, Wensong; et al. An Integrated Boost Resonant Converter for Photovoltaic Applications. IEEE Transactions on Power Electronics. v. 32, n. 3. 2013.

YU, Yuan; LEE, Fred C.Y; TRINER, James E. Power Converter Design Optimization. IEEE Transactions on Aerospace and Electronic Systems. v. 15, n. 3. 1979.

ZHANG, J; et. al. Decoupled optimization technique for design of switching regulators using genetic algorithms. Anais da IEEE International Conference Circuits and Systems. Geneva, Switzerland, v. 3. pp. 495–498. 2000.
 