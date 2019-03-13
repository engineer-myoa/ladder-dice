import dice
import time
from configparser import ConfigParser
import slacker
from flask import Flask, request

IGNORED_USER = []
APP_CONFIG = "app.config"
app = Flask(__name__)


def configInit():
    config = ConfigParser()
    config.add_section("TOKEN")
    config.add_section("IGNORED_USER")
    config.add_section("SERVER")
    config["TOKEN"]["slack.api.token"] = ""
    config["TOKEN"]["slack.bot.token"] = ""
    config["IGNORED_USER"]["app.user.ignored"] = ""
    config["SERVER"]["app.channels.allowed"] = ""

    with open(APP_CONFIG, "w") as f:
        config.write(f)

def excludeAllBot():
    pass

def getChannelMembers(channelName):
    conversationInfo = slack.conversations.members(channelName)
    print(conversationInfo)
    if conversationInfo.body["ok"] != True:
        return False

    members = conversationInfo.body["members"]
    return members

def filteredMembers(members: list):
    idx = 0
    while idx < len(members):
        if members[idx] in IGNORED_USER:
            members.pop(idx)
            continue

        idx += 1

    return members

@app.route("/add_ignore", methods=["POST"])
def addIgnoreUser():
    body = request.values
    commandArguments = body["text"].split(" ")
    print(commandArguments)

    getAllUserList = slack.users.list().body["members"]
    userDict = {}
    for userInfo in getAllUserList:
        userDict[userInfo["name"]] = userInfo["id"]

    for userId in commandArguments:
        userId = userId.lstrip("@")
        config["IGNORED_USER"]["app.user.ignored"] = config["IGNORED_USER"]["app.user.ignored"] + userDict[userId] + ";"

    with open(APP_CONFIG, "w") as f:
        config.write(f)
    return "[DICE add ignore result]\n" + "Requester: {0}\n".format(body["user_name"]) + "Ignored below user(s)!\n {0}".format(commandArguments)

def diceRoutine(members, parsedArguments):
    # grant random score
    requestedTime = time.time()
    userDict, infoGraphics = dice.generateRandomDice(members, parsedArguments.get("-c"), requestedTime)
    sortedScoreList = dice.__dictToSortedList__(userDict,
                                            parsedArguments.get("-m"))  # If there is no -m option, will passed None.

    # Mapping high Scored member_id to real_name
    for key, val in sortedScoreList:
        userInfo = slack.users.info(key).body

        name = userInfo["user"]["real_name"]  # TODO: decide to which one use between name(id) and realName(username)
        userDict[name] = userDict.pop(key)  # change key name

    resultString = dice.prettyPrint(userDict, requestedTime, None)

    return resultString

@app.route("/dice", methods=["POST"])
def callback():
    body = request.values
    commandArguments = body["text"].split(" ")

    members = filteredMembers( getChannelMembers(body["channel_id"]) )

    # arguments parsing
    parsedArguments = {}
    for argument in commandArguments:
        argument = argument.split("=")
        if len(argument) != 2:
            continue

        key, val = argument
        parsedArguments[key] = int(val)

    resultString = "[DICE result]\n" + "Requester: {0}\n".format(body["user_name"]) + diceRoutine(members, parsedArguments)

    # TODO Graph
    return resultString

if __name__ == "__main__":
    config = ConfigParser()
    if len(config.read(APP_CONFIG)) == 0:
        configInit()
        print("[INFO] Please fill app.config first :)")
        exit(-1)

    SLACK_BOT_TOKEN = config["TOKEN"]["slack.bot.token"]
    IGNORED_USER = config["IGNORED_USER"]["app.user.ignored"].split(";")
    slack = slacker.Slacker(SLACK_BOT_TOKEN)

    app.run(host="10.70.19.186", port=41410)
