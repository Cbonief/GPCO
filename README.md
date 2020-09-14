
# GPCO - General Power Converter Optimizer
Written by **Carlos Bonifácio Eberhardt Franco**

GPCO is a python based efficiency optimizer for switched-mode power converters that is able to optimize both the operating frequency and the components used, while satisfying the design constraints. It does this by separating the discrete and continuous variables into two layers of optimization.
The superficial layer uses a genetic algorithm to handle the discrete variables, while the second layer uses a numeric, gradient based algorithm to optimize the continuous variables.

* Obs: Up until this point, the only power converter available is the Boost Half Bridge DC-DC converter (Figure 1). However, the code is being generalized to easily accept other converters in the near future.

*Figure 1 - Boost Half Bridge DC-DC Converter*

![Hello](https://i.imgur.com/MKGG5rW.png)


## 1. Description of the problem
The problem of optimizing a converter's characteristic while satisfying design and physical constraints can be mathematically write as:

![](https://i.imgur.com/jzpz3OZ.gif)

Where X are all the converter's parameters that are considered free in the optimization, R are the performance requirements, such as: <img src="https://render.githubusercontent.com/render/math?math=V_i">, <img src="https://render.githubusercontent.com/render/math?math=V_o">, <img src="https://render.githubusercontent.com/render/math?math=\Delta_o">, etc. And finally K are component related restrictions and parameters, such as the maximum reverse voltage on a diode.

In the GPCO,  <img src="https://render.githubusercontent.com/render/math?math=\small F(X,R,K)"> is the efficiency of the converter, X are all components, switching frequency and inductance values. Some parameters, such as the value of the capacitances are not in X because the whole capacitor already is, and that include it's capacitance.

And <img src="https://render.githubusercontent.com/render/math?math=\small H(X,R,K)"> are all the restrictions of the converter, which include the maximum variation of the output voltage, the maximum magnetic induction permitted on the core of any inductor and many others.

## 2. Main Algorithm

### 2.1 Genetic Algorithm
As mentioned, the first layer of the algorithm is a simple GA (Genetic Algorithm), such as the one on the Figure 2, where the fitness of each individual is it's efficiency. The variables being optimized by this layer are the discrete components of the power converter: switches, diodes, capacitors and even the cores and cables of any inductor or transformer present on the circuit. Also included in this layer are the number of windings and parallel conductors on the inductors/transformers, both being considered to be integer only. 

*Figure 2 - Genetic Algorithm Flow Chart.*

![enter image description here](https://i.imgur.com/gPqnEkX.jpg)


## 2.2 Numeric Algorithm
The step "Test Population" is when the gradient based algorithm get's used, because the fitness that get's passed to the GA is actually the best efficiency possible for that set of discrete variables. This is the second layer of optimization, based on the continuous variables of the converter, which are: switching frequency and the value of the inductances.

In the GPCO the default numeric optimizer for this layer is SLSQP (Sequential Least Square Quadratic Programming), using the package SciPy. But in fact any optimizer that is able to deal with inequality constraints is suitable for the job. Some examples of these type of optimizers are: COBYLA, SUMT and ALAG.

## 3. How to components are implemented
The class diagram

*Figure 3 -  Components Class Diagram*

![enter image description here](https://i.imgur.com/48baHHL.jpg)

## 4. Converter Implementation 
