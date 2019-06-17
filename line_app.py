import datetime
import json

from sqlalchemy.orm import sessionmaker, scoped_session

import dice
import time
from flask import Flask, request, abort
from flask.json import jsonify

from configparser import ConfigParser

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
)

from db import model


CONFIG_FILE_PATH = "app.config"

app = Flask(__name__)

config = ConfigParser()
config.read(CONFIG_FILE_PATH)

CHANNEL_ACCESS_TOKEN = config["TOKEN"]["line.access.token"]
CHANNEL_SECRET = config["TOKEN"]["line.channel.secret"]
IMAGE_URL_PREFIX = config["SERVER"]["image.url.prefix"]
ADMIN_USER_ID = config["USER"]["line.admin.userId"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/")
def index():
    return "HELL WORLD"


@app.route("/push", methods=["POST"])
def push():
    jsonData = request.json
    print(jsonData)

    returnJson = {}

    roomId = jsonData["room_id"]
    msgBody = jsonData["msg_body"]
    msgType = jsonData["msg_type"]

    if msgType != "text":
        returnJson["code"] = 400
        returnJson["msg"] = "this msg type is not supported"
        return jsonify(returnJson)

    pushMessage(roomId, msgBody, msgType)

    returnJson["code"] = 200
    returnJson["msg"] = "successfully pushing message"
    return jsonify(returnJson)


def pushMessage(channelId, msgBody, msgType):
    msg = None
    if msgType == "text":
        msg = TextSendMessage(text=msgBody)
    elif msgType == "image":
        msg = ImageSendMessage(original_content_url=msgBody["original"], preview_image_url=msgBody["thumbnail"])
    else:
        return
    line_bot_api.push_message(channelId, msg)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    jsonData = json.loads(body)
    # print(jsonData)

    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)

    except InvalidSignatureError as e:
        print(e)
        abort(400)

    return 'OK'


class ChannelUtil:

    @staticmethod
    def getMembers(channelId, type):
        if type == "room":
            return line_bot_api.get_room_member_ids(channelId, timeout=10)
        elif type == "group":
            return line_bot_api.get_group_member_ids(channelId, timeout=10)
        return None

    @staticmethod
    def parseChannelId(eventSource):
        type = eventSource.type
        if type == "room":
            return eventSource.room_id
        elif type == "group":
            return eventSource.group_id
        elif type == "user":
            return eventSource.user_id


def commandDice(event, command):
    try:
        channelId = ChannelUtil.parseChannelId(event.source)
        channelType = event.source.type
        if channelType == "user":
            return None
    except  Exception as e:
        print(e)

    # members = ChannelUtil.getMembers(channelId, channelType)

    requestedTime = time.time()
    diceMembers = session.query(model.DiceMember).all()
    if len(diceMembers) <= 0:
        return "[{0}]\nThere is no member. Please add member first.".format(datetime.datetime.now())

    diceMemberNames = list(map(lambda x: x.name, diceMembers))

    import random
    random.shuffle(diceMemberNames)
    userDict = dice.generateRandomDice(diceMemberNames)
    resultString = dice.prettyPrint(userDict, requestedTime, 8)

    sortedResultList = dice.__dictToSortedList__(userDict)
    matchedUser: model.DiceMember = list(filter(lambda x: x.name == sortedResultList[0][0], diceMembers))[0]

    diceResult = model.DiceResult(resultString, matchedUser.id)
    session.add(diceResult)
    session.commit()

    resultGraphFileName = dice.prettyGraph(userDict, 8)
    pushMsgBody = {"original": IMAGE_URL_PREFIX + resultGraphFileName,
                   "thumbnail": "https://myoa-engineering.com/linebot-ladder/graphs/logo.jpg"}
    pushMessage(channelId, pushMsgBody, "image")

    return resultString


def __commandParser__(event):
    print(event)
    command = event.message.text.strip().split(" ")
    userId = event.source.user_id

    if command[0] == "/dice":
        command = [] if len(command) == 0 else command[1:]
        resultString = "[DICE result]\n" + commandDice(event, command)
        return resultString
    elif command[0] == "/add" and userId == ADMIN_USER_ID:
        addcompletedMembers = []
        alreadyExistMembers = []
        for username in command[1:]:

            if session.query(model.DiceMember).filter_by(name=username).count() > 0:
                alreadyExistMembers.append(username)

            newMember = model.DiceMember(username)
            session.add(newMember)
            session.commit()
            addcompletedMembers.append(username)

        return "[{0}]\n".format(datetime.datetime.now()) \
        + "Member add Successfully : {0}\n\n".format(addcompletedMembers) \
        + "Member already exist : {0}".format(alreadyExistMembers)

    elif command[0] == "/delete" and userId == ADMIN_USER_ID:
        username = command[1]
        if session.query(model.DiceMember).filter_by(name=username).delete() > 0:
            session.commit()
            return "[{0}]\n {1} deleted successfully".format(datetime.datetime.now(), username)

        return "[{0}]\n {1} not exist".format(datetime.datetime.now(), username)

    elif command[0] == "/members":
        diceMembers = session.query(model.DiceMember).all()
        return "[{0}]\n Current DICE Members : {1}"\
            .format(datetime.datetime.now(), str(list(map(lambda x: x.name, diceMembers))))

    elif command[0] == "/status":
        return "NOT IMPLEMENTS"

    return None

# TextMessage에 대해서 Handle하는 Handler
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    resultString = __commandParser__(event)

    if resultString == None:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Not allowed"))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=resultString))

@app.teardown_request
def remove_session(ex=None):
    session.remove()

if __name__ == "__main__":

    conn = model.dataSource.engine.connect()
    session = scoped_session(sessionmaker(bind=model.dataSource.engine))
    # session = Session()

    ssl_context = ("fullchain.pem", "privkey.pem")
    app.run(host="192.168.1.10", port="41410", ssl_context=ssl_context)


