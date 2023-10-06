import random
import copy


def backTrack(CurrentBoard, GlobalBackTrackingSearch, GlobalPossibleValues, newVal):

    global NumNodes
    NumNodes += 1

    BackTrackingSearch = copy.deepcopy(GlobalBackTrackingSearch)
    PossibleValues = copy.deepcopy(GlobalPossibleValues)

    if newVal == -1:
        for idx in range(0, 81):
            if CurrentBoard[idx] == "0":
                PossibleValues[idx] = []
                continue

            cantPick = CurrentBoard[idx]
            row = int(idx / 9)
            column = int(idx % 9)
            for i in range(0, 9):
                BackTrackingSearch[row * 9 + i].add(cantPick)
                BackTrackingSearch[i * 9 + column].add(cantPick)

            row_start = int(row / 3)
            column_start = int(column / 3)

            for x in range(0, 3):
                for y in range(0, 3):
                    BackTrackingSearch[column_start * 3 + (y + row_start * 3) * 9 + x].add(cantPick)


    for key in BackTrackingSearch:
        print(key, BackTrackingSearch[key])

    if len(PossibleValues) == 0:
        return CurrentBoard

    states = []
    for key in PossibleValues:
        possibilities = {"1", "2", "3", "4", "5", "6", "7", "8", "9"} - BackTrackingSearch[key]

        '''
        if len(possibilities) == 0:
            return (False, [])
        '''

        for possibility in possibilities:
            states.append((key, possibility))

    if len(states) == 0:
        return ""


    while len(states) > 0:
        randomVal = random.randrange(0, len(states))
        pick = states[randomVal]
        states.pop(randomVal)

        newBoard = CurrentBoard[0:pick[0]] + pick[1] + CurrentBoard[pick[0] + 1:]

        print(NumNodes)
        #result = backTrack(newBoard, BackTrackingSearch, PossibleValues, pick[0])

        #if result != "":
         #   return result

    return ""


CurrentBoard = ""
FileToRead = "Sudoku/easy.txt"
f = open(FileToRead, "r")

for i in range(0, 9):
    line = f.readline().split('\n')[0].split(",")

    for char in line:
        CurrentBoard += char

print(CurrentBoard)
setSearch = {}
posValues = {}

for y in range(0, 9):
    for x in range(0, 9):
        setSearch[x + y * 9] = set()

NumNodes = 0

print(backTrack(CurrentBoard, setSearch, posValues, -1))
print(NumNodes)