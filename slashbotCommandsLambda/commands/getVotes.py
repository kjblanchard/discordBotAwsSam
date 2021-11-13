from codecs import encode
import json
import boto3
import os
from decimal import Decimal

lambdaArn = os.environ['GETVOTESLAMBDAARN']


def GetDebugRoomVotes(event):
    """Gets the votes from the dynamoDb database and then generates a proper looking discord response

    Args:
        event (json): The interaction event

    Returns:
        json: The json body that we will send back in the interaction event
    """

    question = event.get('data').get('options')[0].get('value')
    data = bytes(json.dumps({
        "question": question
    }).encode('utf-8'))
    client = boto3.client('lambda')
    lambdaResponse = client.invoke(
        FunctionName=lambdaArn,
        Payload=data)
    items = json.loads(lambdaResponse.get('Payload').read()).get('Items')
    falseValues = [item for item in items if item.get(
        'voteType') == Decimal(0)][0].get('votes')
    trueValues = [item for item in items if item.get(
        'voteType') == Decimal(1)][0].get('votes')
    titleText = 'The votes for the debug room are currently....'
    embedText = [
        {
            "author": {
                "name": "Supergoon♫",
                "url": "https://jrpg.supergoon.com",
                "icon_url": "https://i.imgur.com/R66g1Pe.jpg"
            },
            "title": f"The votes are in!!!",
            "url": "https://google.com/",
            "description": "The votes for the debug room are as follows.....",
            "color": 15258703,
            "fields": [
                {
                    "name": "Yes",
                    "value": f"{trueValues}",
                    "inline": True
                },
                {
                    "name": "No",
                    "value": f"{falseValues}",
                    "inline": True
                },
                {
                    "name": "These votes were placed by all players who had an active internet connection and chose a value.",
                    "value": "okay..."
                }
            ],
            "footer": {
                "text": "This notification will self-destruct",
                "icon_url": "https://i.imgur.com/fKL31aD.jpg"
            }
        }
    ]

    responseData = {
        "content": titleText,
        "embeds": embedText
    }

    return responseData
