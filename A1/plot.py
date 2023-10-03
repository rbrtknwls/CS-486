import matplotlib.pyplot as plt
import numpy as np
x = np.ones((1,14))
h1results = [1, 1, 3.6, 12.3, 52.6, 206.6, 941.3,  5002.8, 15710.7, 123394.6, 343869.6, 1982604.5]
h2results = [1, 1, 4,   15.4, 57.4, 225.9, 1053.6, 5832.2, 18735.1, 114533.8, 418689.3, 2020802.0]
h3results = [1, 1, 3.2, 10.2, 36.7, 138.1, 497.5,  2668.7, 8452.2,  58458.9,  203459.1,  918482.0]
plt.ylabel('log(number of nodes expanded)')
plt.xlabel('# of Cities')
plt.show()
