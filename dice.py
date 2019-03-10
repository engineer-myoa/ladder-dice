from slacker import Slacker
import random
import numpy as np
import sys
import datetime, time

RANDOM_ITERATE_COUNT = 5
MAX_SCORE = 100000
MAX_USER = 50
PARAMETER_KEYS = ["-m", "-c" "-v"]


def parseUser(users):
    return dict(zip(users, [0] * len(users)))


def grantScore(size, iterateCount, masterSeed):

    random.seed(masterSeed)
    iterateCount = iterateCount if iterateCount != None else RANDOM_ITERATE_COUNT
    generatedNewSeedList = [ random.randrange(sys.maxsize) for x in range(iterateCount) ]

    adaptiveMaxScore = MAX_SCORE * 1 if size <= MAX_USER else np.floor(np.sqrt(size))

    accumulationScoreResult = [ np.zeros(size, np.uint64) ]
    for seedVal in generatedNewSeedList:
        np.random.seed(seedVal)
        accumulationScoreResult.append(accumulationScoreResult[-1] + np.random.randint(0, MAX_SCORE, size, np.uint64))

    return np.transpose(accumulationScoreResult)

# @TODO
def drawGraph(dictionary):
    print(dictionary)
    pass

def mappingData(users: dict, result):
    resultIdx = 0
    for key in users.keys():
        users[key] = result[resultIdx]
        resultIdx += 1

    return users

def dictToSortedList(dictionary: dict, limit=None):
    size = len(dictionary)

    limit = limit if limit != None else size # check is limit null
    limit = limit if limit < size else size # check is limit not over than dict's length

    return sorted( [[key, val[-1]] for key, val in dictionary.items()], key= lambda val: val[1], reverse=True)[:limit]

def pprint(dictionary, limit=None):
    resultString = ""

    totalScoreList = dictToSortedList(dictionary)
    sumScore = int(np.sum(eachUserScore[-1] for eachUserScore in totalScoreList)) # get last elements and summation all

    size = len(totalScoreList)
    limit = limit if limit != None else size # check is limit null
    limit = limit if limit < size else size # check is limit not over than dict's length

    for k, v in totalScoreList[:limit]:
        resultString += "{0}: {1} pts ({2:2.2f}%)".format(k, v, v/sumScore*100) + "\n"

    return resultString.rstrip()

def generateSeedFromTime(seedTime=None):
    seed = 0

    currTime = seedTime if seedTime != None else time.time()

    currTimeString = str(currTime).replace(".", "")
    leftPart = currTimeString[0 : len(currTimeString)//2]
    rightPart = currTimeString[len(currTimeString)//2:]

    seed += int(leftPart) * int(leftPart[::-1])
    seed += len(currTimeString) // 2 * 10 * int(rightPart) * (int(rightPart) // int(leftPart))

    return seed

def datePretty(timestamp):
    currDateTime = datetime.datetime.fromtimestamp(timestamp)
    return currDateTime.strftime("%Y-%m-%d %H:%M:%S")

def generateRandomDice(users, iterateCount, requestedTime, needGraph):



    seed = generateSeedFromTime(requestedTime)
    userDict = parseUser(users)
    accScoreResult = grantScore(len(userDict), iterateCount, seed)
    mappingData(userDict, accScoreResult) # throw final score

    infoGraphics = None
    if needGraph:
        infoGraphics = drawGraph(userDict)

    return userDict, infoGraphics

if __name__ == "__main__":
    requestedTime = time.time()
    generateRandomDice(['a','b','c','d','e','f'], requestedTime)
