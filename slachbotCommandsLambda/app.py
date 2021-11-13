import commandHandler


def lambda_handler(event, context):
  print(event)
  commandHandler.HandleIncomingCommand(event)
  



