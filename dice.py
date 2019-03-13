from slacker import Slacker
import random
import numpy as np
import datetime, time
import matplotlib.pyplot as plt

SYS_MAX_SIZE = 2**32 - 1
RANDOM_ITERATE_COUNT = 5
MAX_SCORE = 100000
MAX_USER = 50
PARAMETER_KEYS = ["-m", "-c" "-v"]
ASCII_MAX_LENGTH = 50

def __parseUser__(users):
	return dict(zip(users, [0] * len(users)))

def __optionalIndexBound__(idx: int, iterableObject: [list, dict]):
	size = len(iterableObject)
	idx = idx if idx != None else size # check is limit null
	idx = idx if idx < size else size # check is limit not over than dict's length
	return idx
	
def __grantScore__(size, iterateCount, masterSeed):

	random.seed(masterSeed)
	iterateCount = iterateCount if iterateCount != None else RANDOM_ITERATE_COUNT
	generatedNewSeedList = [ random.randrange(SYS_MAX_SIZE) for x in range(iterateCount) ]
	print(generatedNewSeedList)

	adaptiveMaxScore = MAX_SCORE * 1 if size <= MAX_USER else np.floor(np.sqrt(size))

	accumulationScoreResult = [ np.zeros(size, np.uint64) ]
	for seedVal in generatedNewSeedList:
		np.random.seed(seedVal)
		accumulationScoreResult.append(accumulationScoreResult[-1] + np.random.randint(0, adaptiveMaxScore, size, np.uint64))

	return np.transpose(accumulationScoreResult)

def __drawAsciiArt__(percentage: float):
	size = int(ASCII_MAX_LENGTH * percentage)
	return "|" * size

def __mappingData__(users: dict, result):
	resultIdx = 0
	for key in users.keys():
		users[key] = result[resultIdx]
		resultIdx += 1

	return users

def __dictToSortedList__(dictionary: dict, limit=None):
	limit = __optionalIndexBound__(limit, dictionary)

	return sorted( [[key, val] for key, val in dictionary.items()], key= lambda val: val[1][-1], reverse=True)[:limit]

def prettyGraph(dictionary, limit=None):
	ticks = np.arange(1, RANDOM_ITERATE_COUNT+1,1)
	plt.xticks(ticks)

	totalScoreList = __dictToSortedList__(dictionary, limit)

	for key, val in totalScoreList:
		val = val[1:] # exclude 0 round
		plt.plot(ticks, val, label=key, marker="o")
	
	plt.legend(loc=4)
	plt.xlabel("round")
	plt.ylabel("score")
	plt.show()
	return 0
	
def prettyPrint(dictionary, requestedTime, limit=None):
	resultString = ""

	totalScoreList = __dictToSortedList__(dictionary, limit)
	print(totalScoreList)
	sumScore = np.sum(np.fromiter( [eachUserScore[-1] for _, eachUserScore in totalScoreList], np.uint64) ) # get last elements and summation all

	for k, v in totalScoreList:
		v = v[-1] # get last item
		ratio = v/sumScore
		percentage = ratio*100
		resultString += "{0:<15} :: {1:<{2}} :: {3} pts ({4:2.2f}%)".format(k, __drawAsciiArt__(ratio), int(ASCII_MAX_LENGTH*0.5), v, percentage) + "\n"

	return "Timestamp: {0}\n\n".format(__datePretty__(requestedTime)) + resultString.rstrip()

def __generateSeedFromTime__(seedTime=None):
	seed = 0

	currTime = seedTime if seedTime != None else time.time()
	currTimeString = str(currTime).replace(".", "")
	leftPart = currTimeString[0 : len(currTimeString)//2]
	rightPart = currTimeString[len(currTimeString)//2:]

	seed += int(leftPart) * int(leftPart[::-1])
	seed += len(currTimeString) // 2 * 10 * int(rightPart) * (int(rightPart) // int(leftPart))
	return seed

def __datePretty__(timestamp):
	currDateTime = datetime.datetime.fromtimestamp(timestamp)
	return currDateTime.strftime("%Y-%m-%d %H:%M:%S")

def generateRandomDice(users, iterateCount, requestedTime):
	seed = __generateSeedFromTime__(requestedTime)
	userDict = __parseUser__(users)
	accScoreResult = __grantScore__(len(userDict), iterateCount, seed)
	__mappingData__(userDict, accScoreResult) # throw final score

	return userDict

if __name__ == "__main__":
	requestedTime = time.time()
	userDict = generateRandomDice(['a','b','c','d','e','f'], None, requestedTime)
	resultString = prettyPrint(userDict, requestedTime,3)
	resultGraph = prettyGraph(userDict, 3)
	print(resultString)
