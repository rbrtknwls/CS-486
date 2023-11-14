import numpy as np

ps = 0.1
pr = 0.2

discount = 0.95

Payoffs = [0, 0, 0, 10, -10]
Transitions = [[0.1, 0.9,    0.9,      0,   0],
               [0,    ps,   1-ps,      0,    0],
               [0,     0,    0.1, 0.9-pr,   pr],
               [0.9,   0,      0,    0.1,    0],
               [0.9,   0,      0,      0,  0.1]]
'''
Payoffs = [0, 0, 10, 10]

Transitions = [[[0.5, 0.5,   0,   0], [  1,   0,   0,   0]],
               [[  0,   1,   0,   0], [0.5,   0,   0, 0.5]],
               [[  0, 0.5, 0.5,   0], [0.5,   0, 0.5,   0]],
               [[  0,   1,   0,   0], [  0,   0, 0.5, 0.5]]]
'''
discount = 0.9
current = Payoffs;

threshold = 0.000000001


for i in range(0, 1000):
    new = [0,0,0,0,0]

    for currentState in range(0, len(Payoffs)):
        new[currentState] += Payoffs[currentState]
        if currentState == 0:

            a = discount * current[1] * Transitions[0][1]
            b = discount * current[2] * Transitions[0][2]

            print ("a: ", a, " | b:", b)
            new[0] += max(a,b)
            new[0] += discount * current[0] * Transitions[0][0]
        else:
            for transitionState in range(0, len(Payoffs)):
                new[currentState] += discount * current[transitionState] * Transitions[currentState][transitionState]

    diff = 0
    for val in range(0, len(current)):
        diff += np.abs(current[val] - new[val])
    if diff < threshold:
        break
    current = new
    

'''
for i in range(0, 3):
    new = [0,0,0,0]
    print(i, " => ", end="")
    for currentState in range(0, len(Payoffs)):
        new[currentState] += Payoffs[currentState]
        a = 0
        s = 0
        for transitionState in range(0, len(Payoffs)):

            a += discount * current[transitionState] * Transitions[currentState][0][transitionState]
            s += discount * current[transitionState] * Transitions[currentState][1][transitionState]

        new[currentState] += max(a, s)

        if (a >= s):
            print(" A ", a, " ", end="")
        else:
            print(" S ", s, " ", end="")

        print(round(new[currentState],2), "|", end="")
    print("")

    diff = 0
    for val in range(0, len(current)):
        diff += np.abs(current[val] - new[val])
    if diff < threshold:
        break
    current = new
    
'''
print(current)