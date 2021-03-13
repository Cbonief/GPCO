import math
import numpy as np

def truncate(number, decimals=0):

    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor


def get_number_of_decimals(data):
    return len(str(int(100*truncate(data, 2)))) - int(np.ceil(np.log10(data)))

x = 0.89
y = 0.5
epoch = 252

k = str(100*truncate(x, 2)+(10**5)*get_number_of_decimals(x))
result = int(k[1:6])/(10**(int(k[0])))

print(result)


print(100*truncate(x, 2)+(10**5)*get_number_of_decimals(x))

result = (10**13)*truncate(x, 2) + (10**16)*get_number_of_decimals(x)
result += (10**7)*truncate(y, 2) + (10**10)*get_number_of_decimals(y)
result += epoch
result = int(result)

print(result)

def get_data_from_int(data):
    aux = str(data)
    x = int(aux[1:6])/(10**(int(aux[0])))
    y = int(aux[7:12])/(10**(int(aux[6])))
    epoch = int(aux[13:])
    return x, y, epoch

print(get_data_from_int(result))