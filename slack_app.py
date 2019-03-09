import dice
import time


from slacker import Slacker

SLACK_API_TOKEN = "Jrs9vr6e0EP2ywNnCcZMZEhB"
BOT_TOKEN = "xoxb-48712680069-572865732823-bJkLx3fRcrqhv1ZVBVD4lT0j"
slack = Slacker(BOT_TOKEN)

# Send a message to #general channel

# Get users list
response = slack.users.list()
if response.body == False:
    exit(-1)
members = response.body['members']

def extractNameFromMembers(members):
    names = []
    for member in members:
        if member["real_name"] in ["**Bot", "**bot"]:
            continue
        names.append( member["real_name"] )
    return names


names = extractNameFromMembers(members)
result, infoGraphics = dice.generateRandomDice(names, time.time(), False)

slack.chat.post_message('#s-mirror-notice', result)


# Upload a file
# slack.files.upload('hello.txt')

# Advanced: Use `request.Session` for connection pooling (reuse)
# from requests.sessions import Session
# with Session() as session:
#     slack = Slacker(token, session=session)
#     slack.chat.post_message('#s-mirror-notice', 'All these requests')
