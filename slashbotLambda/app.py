import json
import boto3
import logging
import os
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
apiBotPublicKey = os.environ['BOTPUBLICKEY']
commandsApiArn = os.environ['COMMANDAPIARN']


def lambda_handler(event, context):
    """This lambda function handles Discord authentication requests from them.  It verifies their key, and responds to ping and Interactions from our bot.  
    Discord has a limitation that we must respond in 3 seconds, due to this if it is a command we will pass back a 
    temporary value so that our bot "thinks about it" and then the command backend will update it.


    Args:
        event (json): The event json that is passed in from the api gateway.
        context (json): The context that is passed in from the api gateway.

    Raises:
        Exception: Throws an exception if the signature is bad, and sends Discord a 401 error.  
        This is required for discord's authentication as they will send bad auth requests to test it.

    Returns:
        json: The response that we will send back through to the sender
    """
    logger.info('## EVENT')
    logger.info(event)
    logger.info('## Context')
    logger.info(context)

    try:
        VerifySignature(event, apiBotPublicKey)
    except BadSignatureError:
        return {
            'statusCode': 401,
            'body': "Invalid Signature"
        }

    if(HandleDiscordPing(event)):
        return {
            'statusCode': 200,
            'body': json.dumps({
                'type': 1
            })
        }
    successfulResponse = {
        'statusCode': 200,
        'body': json.dumps({
            'type': 5,
        })
    }
    lambdaData = json.dumps(event.get('body'))
    InvokeDiscordCommandsApi(lambdaData, commandsApiArn)
    return successfulResponse


def VerifySignature(event, botPublicKey):
    """Verifies the signature from the request.  This happens from discords servers occasionally and from each request to see if the request should be processed.  
    We are required to send an unauthorized 401 if this fails.

    Args:
        event (dict): The full raw body from the event as we need the headers and the body
        botPublicKey (string): The bots public key
    """
    signature = event['headers']['x-signature-ed25519']
    timestamp = event['headers']['x-signature-timestamp']
    body = event['body']
    message = (timestamp + body).encode()
    verify_key = VerifyKey(bytes.fromhex(botPublicKey))
    verify_key.verify(message, bytes.fromhex(signature))

def HandleDiscordPing(body):
    """This handles the pings that the discord api automatically sends frequently to this endpoint for testing

    Args:
        body httpRequest: Body of the message that is sent

    Returns:
        bool: True if it is a ping, false if it isnt.
    """
    if json.loads(body.get("body")).get("type") == 1:
        return True
    return False


def InvokeDiscordCommandsApi(payloadData, lambdaToInvokeArn):
    """Invokes our lambda commands API to handle the command asyncronously so that we don't time out, and send the token and the command with it.

    Args:
        payloadData (json): The json that should be sent to the lambda function to parse through and handle the command.  
        Needs the token for the interaction and the actual command that was sent at the minimum.

        lambdaToInvokeArn (string): The lambda function that should be invoked

    """
    lambdaClient = boto3.client('lambda')
    lambdaClient.invoke(
        FunctionName=lambdaToInvokeArn,
        InvocationType='Event',
        Payload=payloadData)


