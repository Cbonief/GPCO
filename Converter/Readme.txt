This folder contains all classes and functions related to:
- Creating and simulating the Boost Half Bridge Inverter.
- Obtaining the converter total loss.
- Calculate all the converter restriction functions.
- Optimizing the converter loss in terms of frequency and inductances.

All other converter variables such as: capacitors, diodes, winding number, number of parallel cables, are considered
fixed in this optimization. They're in fact optimized in the Optimizer.py file, in which a genetic algorithm is employed
to find the best combination of of capacitors, diodes, switches, magnetic cores, cables, winding number, number of
parallel cables.