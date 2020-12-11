import numpy as np

x = np.e

for i in range(0, 100):
	print(np.floor(x))
	x = np.floor(x)*(x-np.floor(x)+1)