import matplotlib.pyplot as plt
from statistics import mean
import numpy as np
x = []
for i in range(1, 14):
    x.append(i)
print(x)

x = np.array(x)
h1results = np.array(np.log([1,1, 1, 3.6, 12.3, 52.6, 206.6, 941.3,  5002.8, 15710.7, 123394.6, 343869.6, 1982604.5]))
h2results = np.array(np.log([1,1, 1, 4,   15.4, 57.4, 225.9, 1053.6, 5832.2, 18735.1, 114533.8, 418689.3, 2020802.0]))
h3results = np.array(np.log([1,1, 1, 3.2, 10.2, 36.7, 138.1, 497.5,  2668.7, 8452.2,  58458.9,  203459.1,  918482.0]))


def best_fit_slope_and_intercept(xs, ys):
    m = (((mean(xs) * mean(ys)) - mean(xs * ys)) /
         ((mean(xs) * mean(xs)) - mean(xs * xs)))

    b = mean(ys) - m * mean(xs)

    return m, b


m2, b2 = best_fit_slope_and_intercept(x, h2results)
m1, b1 = best_fit_slope_and_intercept(x, h1results)

leftOver = []
h1predicted = []
h2predicted = []
h3predicted = []
x3 = [14, 15, 16]
more = np.array([4323873, 9521119,21013284])
more = np.log(more)
a = np.array(np.concatenate((h3results, more), axis=0))
print(a)
m3, b3 = best_fit_slope_and_intercept(np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]), a)
leftovetB = []
for i in range(13, 33):
    leftOver.append(i)
    if (i > 15):
        leftovetB.append(i)
        h3predicted.append(i*m3 + b3 + 0.5)
    h2predicted.append(i*m2 + b2)
    h1predicted.append(i*m1 + b1)

print(32*m3 +b3)
print(32*m2 +b2)
print(32*m1 + b1)
'''
plt.plot(leftOver, h1predicted, "b--", label = "Heuristic #1 (Predicted)")
plt.plot(leftOver, h2predicted, "r--", label = "Heuristic #2 (Predicted)")
plt.plot(leftovetB, h3predicted, "g--", label = "Heuristic #3 (Predicted)")
'''

xn = np.array(np.concatenate((x,x3)))
h3results = np.array(np.concatenate((h3results,more)))
plt.plot(x, h1results ,"bo-",  label= "Heuristic #1 (Actual)")
plt.plot(x, h2results ,"ro-", label= "Heuristic #2 (Actual)")
plt.plot(xn, h3results ,"go-", label= "Heuristic #3 (Actual)")
plt.ylabel('log(Number of Nodes Expanded)')
plt.xlabel('Number of Cities')
plt.legend()
plt.title("Number of Cities on Nodes Expanded (Observed)")
plt.show()
