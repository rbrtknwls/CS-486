import numpy as np
import heapq


cityMap = {}                                                  # Store position of each city
stateCostMap = {}                                             # Store total cost of each state
cityMinCost = {}                                              # Store minimum cost of each city

states = []                                                   # Stores our states to expand
citiesToVisit = []                                            # Stores the cities we haven't visited

# This function takes in two city and calculates the distance between them (l2 norm)
def calculateCost(city1, city2):
    city1cords = cityMap[city1]
    city2cords = cityMap[city2]

    return np.sqrt((city1cords[0] - city2cords[0]) ** 2 + (city1cords[1] - city2cords[1]) ** 2)


# This is the third heuristic, the cost of the state + the distance to each possible next city
def getCost3(state):
    return calculateCost(state[-2], state[-1]) + stateCostMap[state[0:-1]]

# This is the second heuristic, the cost of the state + 0
def getCost2(state):
    return stateCostMap[state[0:-1]]

# This is the first heuristic, the cost of the state + the minimum distance to the current state
def getCost1(state):
    return cityMinCost[city] + stateCostMap[state[0:-1]]


# db refers to the number of cities we need to loop through
#for db in range(2, 14):
numberOfStates = 0                                            # Stores total states for problem set

db = 16
for instance in range(1, 2):

    # Empty out our global variables
    cityMap = {}
    stateCostMap = {}
    cityMinCost = {}
    states = []
    citiesToVisit = []

    # Read in the file
    file = open("randTSP/" + str(db) + "/instance_" + str(instance) + ".txt", "r")
    numberOfCities = int(file.readline())

    states = []
    heapq.heapify(states)                                     # States is a heap so we do our operations quickly
    finalGoalString = []

    # Convert the points in the text file into our dictionaries
    for i in range(0, numberOfCities):
        line = file.readline().split(" ")
        line[2] = line[2].split('\n')[0]

        if line[0] == 'A':
            stateCostMap['A'] = 0
        else:
            citiesToVisit.append(line[0])
        finalGoalString.append(line[0])
        cityMap[line[0]] = (int(line[1]), int(line[2]))

    listOfAllCites = citiesToVisit + ["A"]

    # Manually calculate the children from the first node
    for cityRef in citiesToVisit:
        minSize = -1
        for city in listOfAllCites:
            if (cityRef != city):
                currSize = calculateCost(city, cityRef)
                if (minSize == -1 or minSize > currSize):
                    minSize = currSize
        cityMinCost[cityRef] = minSize

    for city in citiesToVisit:
        newState = "A" + city
        # Add the distance + state representation onto the heap for later
        heapq.heappush(states, (getCost3(newState), newState))

    while True:
        numberOfStates += 1

        # Pop the closest state
        curPick = heapq.heappop(states)[1]

        count = 0
        # Add its children to the heap
        for city in citiesToVisit:
            if city not in curPick:
                actualCost = calculateCost(curPick[-1], city)
                stateCostMap[curPick] = actualCost + stateCostMap[curPick[0:-1]]
                newState = curPick + city
                heapq.heappush(states, (getCost3(newState), newState))
                count += 1

        if count <= 1:
            break

print("City " + str(db) +"#: " + str(numberOfStates))