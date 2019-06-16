import datetime
import json

from sqlalchemy.orm import sessionmaker

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

IMAGE_URL_PREFIX = "mock"
CHANNEL_ACCESS_TOKEN = "mock"
CHANNEL_SECRET = "mock"

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

    if command[0] == "/dice":
        command = [] if len(command) == 0 else command[1:]
        resultString = "[DICE result]\n" + commandDice(event, command)
        return resultString
    elif command[0] == "/add":
        username = command[1]
        newMember = model.DiceMember(username)
        session.add(newMember)
        session.commit()
        return "[{0}] Member add Successfully : {1}".format(newMember.reg_dtime, newMember.name)
    elif command[0] == "/delete":
        username = command[1]
        session.query(model.DiceMember).filter(username=username).delete()
        session.commit()
        return "[{0}] {1} deleted successfully".format(datetime.datetime.now(), username)

    elif command[0] == "/status":
        return "NOT IMPLEMENTS"


def testParser(data: str):
    print(data)
    command = data.strip().split(" ")

    if command[0] == "/dice":
        command = [] if len(command) == 0 else command[1:]
        resultString = "[DICE result]\n" + commandDice(None, command)
        return resultString

    elif command[0] == "/add":
        username = command[1]
        newMember = model.DiceMember(username)
        session.add(newMember)
        session.commit()
        return "[{0}] {1}, add successfully".format(newMember.reg_dtime, newMember.name)

    elif command[0] == "/delete":
        username = command[1]
        session.query(model.DiceMember).filter_by(name=username).delete()
        session.commit()
        return "[{0}] {1} deleted successfully".format(datetime.datetime.now(), username)


    elif command[0] == "/status":
        return "NOT IMPLEMENTS"


# TextMessage에 대해서 Handle하는 Handler
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    resultString = __commandParser__(event)

    if resultString == None:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="NO"))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=resultString))


if __name__ == "__main__":
    config.read(CONFIG_FILE_PATH)

    CHANNEL_ACCESS_TOKEN = config["TOKEN"]["line.channel.secret"]
    CHANNEL_SECRET = config["TOKEN"]["line.access.token"]
    IMAGE_URL_PREFIX = config["SERVER"]["image.url.prefix"]

    conn = model.dataSource.engine.connect()
    Session = sessionmaker(bind=model.dataSource.engine)
    session = Session()

    ssl_context = ("fullchain.pem", "privkey.pem")
    app.run(host="192.168.0.100", port="41410", ssl_context=ssl_context)


