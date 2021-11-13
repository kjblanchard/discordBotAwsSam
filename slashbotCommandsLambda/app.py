from enum import Enum
import json
import urllib3
import os
import logging
from commands.getVotes import GetDebugRoomVotes

logger = logging.getLogger()
logger.setLevel(logging.INFO)
baseurl = 'https://discord.com/api/webhooks'
appId = os.environ['SLASHBOTAPPID']


def lambda_handler(event, context):
    """This function handles all of the commands our bot can react to.  This is called by our frontend and passes in a specific interaction that we will be responding to to update.

    Args:
        event (json): The event that we will be responding to, passed in from the front end lambda function and includes the interaction we will respond to
        context (json): The context passed in from aws
    """
    print(event)
    eventDict = json.loads(event)
    HandleIncomingCommand(eventDict)

class CommandEnum(Enum):
    """An enum so that we can process the commands without referencing their real names if need be

    Args:
        Enum (type): the type of this class
    """
    wave = 'wave'
    getvotes = 'getvotes'

def HandleIncomingCommand(eventjson):
    """Processes the command event, and returns a request to the interaction based on the type

    Args:
        eventjson (dictionary): The python dictionary that we will parse through to get the data
    """
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
    logger.info(item.read())

def createFullUrl(token):
    return f'{baseurl}/{appId}/{token}'

def GetCommandResponseDataSwitch(command, event):
    """Returns the response that we should send back to the interaction.  This will be extended from the 'commands' folder where we will add in our commands

    Args:
        command (string): The command that we received from our request
        event (json): The json event we received, this is passed into our commands and used to generate the response data

    Returns:
        [json]: The actual response body that is used to send back to the interaction we are updating.
    """
    if(command == CommandEnum.wave.value):
        return {"content": "Hello, world!"}
    elif(command == CommandEnum.getvotes.value):
        return  GetDebugRoomVotes(event)
    else:
        return {"content": "Somehow this command doesn't have a switch for it yet, oops!"}  



