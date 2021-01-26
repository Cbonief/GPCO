# Numeric Optimizer

All other converter variables such as: capacitors, diodes, winding number, number of parallel cables, are considered
fixed in this optimization.

To use the numeric optimizer, call the function `optimize_converter`, using a converter as input.
The function will return three variables:
1. Minimal obtained loss.
2. Success flag (False if couldn't optimize or if converter is unfeasible).
3. Solution vector.

Additionally, you can give the function the number of tries for the optimization, the number of
subroutine iterations and the optimization method.

**Obs**: since the GPCO is still on early development, the only method that's guaranteed to work is
the default.

## Optimizing The Converter

The problem of optimising the continuous variables of a power converter can be written
mathematically as:

![Optimization Problem](https://i.imgur.com/X1LOx7i.png)

Where **x** is the vector of continuous variables. In the case of the Boost Half Bridge
these variables are:
- Switching Frequency
- Entrance Inductance
- Auxiliary Inductance

With this mathematical description we can define the lagrange multipliers and write a 
Lagrangian function, and solve a different problem, minimizing the Lagrangian instead of **f(x)**.
This Lagrangian is defined as:

![Lagrangian](https://i.imgur.com/wkYdGrn.png)

Now we'll minimize it terms of **x** extended with λ and σ. Although this was presented with
only one equality constraint and one inequality constraint, the same applies if we have a problem
with **P** inequalities and **Q** equalities, then the Lagrangian we'll have a sum of these
constrains functions multiplied by their respective lagrange multiplier. In this way the 
Lagrange Multiplier Method, transforms a constrained optimization problem with **N** variables in an
unconstrained optimization with **N+P+Q** variables.

### Sequential Least Squares

To optimize the converter, the main algorithm used is SLSQP (Sequential Least Squares Quadratic
Programming) in which the algorithm uses a search direction **d** that arises in solving the 
sub-problem:

![SLSQP](https://i.imgur.com/AQ9QyH5.png)

Once this sub-problem is solved, to a certain degree of tolerance, the search direction is then
applied on the original problem.

Every time the sub-problem is formulated, all functions are approximated with a second order
function, and in this way the sub-problem is just a Quadratic Programming Routine, which is 
something that's well understood and relatively easy to solve.