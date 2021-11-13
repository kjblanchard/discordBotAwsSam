import json
import boto3
import logging
from nacl.signing import VerifyKey

publicKeySSMName = '/discord/discordApiBotPublicKey'
commandApiArnSSMName = '/discord/discordCommandLambdaArn'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
  """This is the frontend for our discord bot.  Handles discords security verifying, and hands off the event to our command backend.  It's required to respond within 3 seconds or else discord considers it a failed response.

  Args:
      event (json): The lambda event, it's transformed by the api with a mapping template so that we can verify the signature properly.
      context (json): Passed in by AWS

  Raises:
      Exception: When the verify signature fails.  It will send a 401 when the API gateway receives it.

  Returns:
      [json]: Returns a type 5 response; to discord this means "I acknowledge your message, and will send a response later".
  """
  logger.info('## EVENT')
  logger.info(event)

  (apiBotPublicKey,commandsApiArn) = GetSSMParams()

  try:
    VerifySignature(event, apiBotPublicKey)
  except Exception as e:
    raise Exception(f"Unverified, there was an issue verifying the signature. {e}")
  
  if(HandleDiscordPing(event)):
    return {"type": 1}

  response =   {"type": 5}

  logger.info('## RESPONSE')
  logger.info(response)

  lambdaData = json.dumps(event.get('body-json'))
  InvokeDiscordCommandsApi(lambdaData, commandsApiArn)
  return response

def InvokeDiscordCommandsApi(payloadData, lambdaToInvokeArn):
  """Invokes our lambda commands API to handle the command asyncronously so that we don't time out, and send the token and the command with it.

  Args:
      payloadData (json): The json that should be sent to the lambda function to parse through and handle the command.  Needs the token for the interaction and the actual command that was sent at the minimum.

      lambdaToInvokeArn (string): The lambda function that should be invoked

  """
  lambdaClient = boto3.client('lambda')
  lambdaClient.invoke(
    FunctionName=lambdaToInvokeArn,
    InvocationType='Event',
    Payload=payloadData)

def HandleDiscordPing(body):
    """This handles the pings that the discord api automatically sends frequently to this endpoint for testing

    Args:
        body httpRequest: Body of the message that is sent

    Returns:
        bool: True if it is a ping, false if it isnt.
    """
    if body.get("body-json").get("type") == 1:
        return True
    return False


def VerifySignature(event, botPublicKey):
  """Tries to verify the signature that discord sends frequently to test your endpoint.  This needs an event that was transformed properly by the api gateway as we need the full rawbody to get some of the event to parse, which isn't included otherwise.  This throws an exception if verifykey fails.

  Args:
      event (json): the transformed event from the API gateway so that we can get the output to parse

      botPublicKey (string): The front end bots public key so that we can verify the signature with it.
  """
  signature = event['params']['header']['x-signature-ed25519']
  timestamp = event['params']['header']['x-signature-timestamp']
  raw_body = event.get("rawBody")
  message = timestamp.encode() + raw_body.encode()
  verify_key = VerifyKey(bytes.fromhex(botPublicKey))
  verify_key.verify(message, bytes.fromhex(signature))

def GetSSMParams():
  """Gets the SSM parameters from the store and returns them.

  Returns:
      Both of the parameters as a tuple
  """
  ssm = boto3.client('ssm')
  ssmParams = ssm.get_parameters(
  Names=[
    publicKeySSMName,
    commandApiArnSSMName
  ],
  WithDecryption=True
)
  logger.info(ssmParams )
  return ssmParams.get('Parameters')[0].get('Value'), ssmParams.get('Parameters')[1].get('Value')



