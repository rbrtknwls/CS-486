import numpy as np


class Factor:
    def __init__(self, setOfFactors):
        self.SetOfValues = setOfFactors

    def getAllTerms(self):
        return self.SetOfValues
    def getSizeOfFactor(self):
        return len(self.SetOfValues[0][0])
    def getListOfVariables(self):
        allVariables = set()
        for entry in self.SetOfValues:
            for variable in entry[0]:
                allVariables.add(variable)
        return allVariables

    def getVariable(self, variable):
        numberOfRelivent = []
        for factor in self.SetOfValues:
            listOfVals = set(factor[0])
            if variable in listOfVals:
                numberOfRelivent += [factor]
        return numberOfRelivent

def restrict(factor, variable, value):
    if not value:
        variable = "N" + variable

    terms = factor.getVariable(variable)
    updatedTerms = []
    for term in terms:
        factors = term[0]
        probability = term[1]
        newfactor = []
        for factor in factors:
            if factor != variable:
                newfactor += [factor]

        updatedTerms.append((newfactor, probability))

    return Factor(updatedTerms)


def multiply(factor1, factor2):

    newTerms = []
    largestTerm = max(len(factor1.getAllTerms()[0][0]), len(factor2.getAllTerms()[0][0]))
    for term1 in factor1.getAllTerms():
        for term2 in factor2.getAllTerms():
            combine = set(term1[0]).union(set(term2[0]))
            if len(combine) == largestTerm:
                newTerms.append((list(combine), term1[1]*term2[1]))

    return Factor(newTerms)


def sumout(factor, variable):
    positiveTerms = restrict(factor, variable, True)
    negativeTerms = restrict(factor, variable, False)

    updatedTerms = []
    for posTerm in positiveTerms.getAllTerms():
        for negTerm in negativeTerms.getAllTerms():
            if sorted(posTerm[0]) == sorted(negTerm[0]):
                updatedTerms.append((posTerm[0], negTerm[1]+posTerm[1]))

    return Factor(updatedTerms)

def inference(factorList, queryVarible, orderedListOfHiddenVariables, evidenceList):
    for V in evidenceList:
        print(V)

    for currentVar in orderedListOfHiddenVariables:
        f1 = factorList[0]
        f2 = factorList[0]

        newFactorList = []
        for factor in factorList:
            if currentVar in factor.getListOfVariables():
                if len(factor.getListOfVariables()) == 2:
                    f1 = factor
                else:
                    f2 = factor
            else:
                newFactorList.append(factor)

        f3 = multiply(f1, f2)
        f3 = sumout(f3, currentVar)
        newFactorList.append(f3)
        factorList = newFactorList

    return factorList[0]

def normalize(factor):
    sum = factor.getAllTerms()[0][1] + factor.getAllTerms()[1][1]

    normalized1 = (factor.getAllTerms()[0][0], factor.getAllTerms()[0][1] / sum)
    normalized2 = (factor.getAllTerms()[1][0], factor.getAllTerms()[1][1] / sum)

    return Factor([normalized1, normalized2])

# Values for validation
f1values = ((["A", "B"], 0.9), (["A", "NB"], 0.1), (["NA", "B"], 0.4), (["NA", "NB"], 0.6))
f2values = ((["B", "C"], 0.7), (["B", "NC"], 0.3), (["NB", "C"], 0.8), (["NB", "NC"], 0.2))

g1values = ((["A"], 0.9), (["NA"], 0.1))
g2values = ((["A", "B"], 0.9), (["A", "NB"], 0.1), (["NA", "B"], 0.4), (["NA", "NB"], 0.6))
g3values = ((["B", "C"], 0.7), (["B", "NC"], 0.3), (["NB", "C"], 0.2), (["NB", "NC"], 0.8))

f1 = Factor(g1values)
f2 = Factor(g2values)
f3 = Factor(g3values)

#   FULL MOON
a1values = ((["M"], 1 / 28), (["NM"], 27 / 28))
#   NEIGHBOUR IS AWAY
a2values = ((["N"], 0.3), (["NN"], 0.7))
#   NEIGHBOURS DOG IS HOWLING
a3values = ((["M", "N", "D"], 0.8), (["M", "N", "ND"], 0.2),
            (["M", "NN", "D"], 0.4), (["M", "NN", "ND"], 0.6),
            (["NM", "N", "D"], 0.5), (["NM", "N", "ND"], 0.5),
            (["NM", "NN", "D"], 0), (["NM", "NN", "ND"], 1))

FM = Factor(a1values)
NA = Factor(a2values)
NDG = Factor(a3values)
NDG = inference([FM, NA, NDG], "D", ["M", "N"], [])

#   FIDO IS SICK
a4values = ((["S"], 0.05), (["NS"], 0.95))
#   FIDO HOWLS
a5values = ((["S", "M", "D", "H"], 0.99), (["S", "M", "D", "NH"], 0.01),
            (["S", "M", "ND", "H"], 0.9), (["S", "M", "ND", "NH"], 0.1),
            (["S", "NM", "D", "H"], 0.75), (["S", "NM", "D", "NH"], 0.25),
            (["S", "NM", "ND", "H"], 0.5), (["S", "NM", "ND", "NH"], 0.5),
            (["NS", "M", "D", "H"], 0.65), (["NS", "M", "D", "NH"], 0.35),
            (["NS", "M", "ND", "H"], 0.4), (["NS", "M", "ND", "NH"], 0.6),
            (["NS", "NM", "D", "H"], 0.2), (["NS", "NM", "D", "NH"], 0.8),
            (["NS", "NM", "ND", "H"], 0), (["NS", "NM", "ND", "NH"], 1))

FS = Factor(a4values)
FH = Factor(a5values)

FH = inference([FH, FS, FM, NDG], "H", ["D", "M", "S"], [])
print(normalize(FH).getAllTerms())

