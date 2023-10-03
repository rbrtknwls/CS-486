import numpy as np
import heapq

cityMap = {}
stateCostMap = {}
states = []
citiesToVisit = []
cityMinCost = {}


def calculateCost(city1, city2):
    city1cords = cityMap[city1]
    city2cords = cityMap[city2]

    return np.sqrt((city1cords[0] - city2cords[0]) ** 2 + (city1cords[1] - city2cords[1]) ** 2)


# This is our "empty" heuristic which will always just return 0
def getCost3(state):
    return calculateCost(state[-2], state[-1]) + stateCostMap[state[0:-1]]


def getCost2(state):
    return stateCostMap[state[0:-1]]


def getCost1(state):
    return cityMinCost[city] + stateCostMap[state[0:-1]]


for db in range(2, 14):
    numberOfStates = 0
    for instance in range(1, 11):

        cityMap = {}
        stateCostMap = {}
        states = []
        citiesToVisit = []

        cityMinCost = {}
        file = open("randTSP/" + str(db) + "/instance_" + str(instance) + ".txt", "r")
        numberOfCities = int(file.readline())

        states = []
        heapq.heapify(states)
        finalGoalString = []

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
            heapq.heappush(states, (getCost3(newState), newState))

        while True:
            numberOfStates += 1

            curPick = heapq.heappop(states)[1]

            count = 0
            for city in citiesToVisit:
                if city not in curPick:
                    actualCost = calculateCost(curPick[-1], city)
                    stateCostMap[curPick] = actualCost + stateCostMap[curPick[0:-1]]
                    newState = curPick + city
                    heapq.heappush(states, (getCost3(newState), newState))
                    count += 1

            if count <= 1:
                break

    print("City " + str(db) +"#: " +str(numberOfStates/10))