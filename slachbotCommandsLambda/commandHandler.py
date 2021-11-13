from enum import Enum
import json
import urllib3
from commands.getVotes import GetDebugRoomVotes
baseurl = 'https://discord.com/api/webhooks'
appId = '907269239184949269'

class CommandEnum(Enum):
    wave = 'wave'
    getvotes = 'getvotes'

def HandleIncomingCommand(eventjson):
    command = eventjson.get('data').get('name')
    token = eventjson.get('token')
    responseData = GetCommandResponseDataSwitch(command, eventjson)

    http = urllib3.PoolManager()
    body= json.dumps(responseData)
    item = http.request(
        'POST',
        createFullUrl(token),
        body=body,
        headers={"Content-Type": "application/json"})

def createFullUrl(token):
    return f'{baseurl}/{appId}/{token}'

def GetCommandResponseDataSwitch(command, event):
    if(command == CommandEnum.wave.value):
        return {"content": "Hello, world!"}
    elif(command == CommandEnum.getvotes.value):
        return  GetDebugRoomVotes(event)
    else:
        return {"content": "Somehow this command doesn't have a switch for it yet, oops!"}
