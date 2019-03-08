from slacker import Slacker
import random
import numpy as np
import sys
import datetime, time

RANDOM_ITERATE_COUNT = 5
MAX_SCORE = 200000
MAX_USER = 50

def parseUser(users):
    return dict(zip(users, [0] * len(users)))


def grantScore(size, masterSeed):
    random.seed(masterSeed)
    generatedNewSeedList = [ random.randrange(sys.maxsize) for x in range(RANDOM_ITERATE_COUNT) ]

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

def pprint(dictionary: dict):
    resultString = ""
    totalScoreList = [ [key, val[-1]] for key, val in dictionary.items() ]
    sumScore = int(np.sum(eachUserScore[-1] for eachUserScore in totalScoreList)) # get last elements and summation all
    totalScoreList = sorted(totalScoreList, key= lambda val: val[1], reverse=True) # sorting based on score
    for k, v in totalScoreList:
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

def generateRandomDice(users, requestedTime):


    seed = generateSeedFromTime(requestedTime)
    userDict = parseUser(users)
    accScoreResult = grantScore(len(userDict), seed)
    mappingData(userDict, accScoreResult) # throw final score
    resultString = "{0} 결과\n\n".format(datePretty(requestedTime)) + pprint(userDict)

    # drawGraph(resultString)

    print(resultString)


requestedTime = time.time()
generateRandomDice(['a','b','c','d','e','f'], requestedTime)
