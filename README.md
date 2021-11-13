# Discord Bot in AWS Serverless model - SAM

![Picture didn't load idiot](https://github.com/kjblanchard/discordBotAwsSam/blob/master/img/demo.gif?raw=true)

## Description
This is an API that works with a discord bot to receive slash commands and respond to them. SAM allows us to test locally while in development, and group everything into a nice cloudformation stack.  It accomplishes this by building the lambdas into docker images and uploads them to ECR when deploying.  

**By using a API gateway that is billed only on usage, and lambda which is billed only on usage, this allows us to have a bot without any hardware, and with minimal costs per month (*pennies*)**

This bot has a command that it responds to with a simple hello world, and a command that calls into a dynamo DB with another lambda function to get some values.  These values are updated in-game from a Unity project.

This discord bot is build in two parts:
* **Front end Lambda**: This lambda function handles Discords authentication requests and pings.  It needs to respond within 3 seconds or else discord will consider it failed.  It is quite easy to fall into the 3 seconds as the cold start times on Lambda functions can add up if you are invoking multiple lambdas like we couuld possibly do.  After the request is verified, it will tell the discord bot to "wait" and send it into a thinking state until we update the response from the command handler.
* **Command Handler**: This lambda function will handle all of our different commands, and update the interaction from the front ends event.

The [template.yaml](template.yaml) file holds the SAM definition.  It's an extension to cloudformation and most cfn will work with it.

## Requirements
* **Route 53 domain**: You need a route 53 domain to use the domain section of the api.  You will need to remove that section if you don't
* **Root certificate** You will need a * cert that you can use for your api's front end in the correct region in AWS certificate manager.
* **A bunch of SSM parameters** Most of the critical information is passed into the SSM parameters inside of the [template.yaml](template.yaml) file in the parameters section.  All of the params are needed and referenced by the lambda functions.
* **A discord application with a bot** Look up on discord developer how to do that
* **Registering the slash commands you want** After you create this *or before* you need to register some commands by using post calls to the discord servers for which slash commands.  This is documented on discord developer as well.
* **AWS cli configured with proper credentials, AWS SAM cli, Python3, and Docker**

## Usage
* **Make sure that you have all the requirements and know what you are doing (*admittedly I failed at this many times*)**: Self explanitory, this is complex.
* **Run sam init**: Sam init creates your template file, generates a s3 bucket to store it in, and gets all of your parameters.
* **Clone the repo**: Pulls in all the functions that you need and the cfn template.
* **Run sam build**: Builds the docker images locally
* **Optional: test locally with sam local start-api**: Wow
* **Run sam deploy to deploy a cloudformation stack**: Pushes your docker images to ecr and creates your stack.

# AWS SAM documentation

## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

You may need the following for local testing.
* [Python 3 installed](https://www.python.org/downloads/)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --guided
```

The first command will build a docker image from a Dockerfile and then copy the source of your application inside the Docker image. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment.

## Use the SAM CLI to build and test locally

Build your application with the `sam build` command.

```bash
sam-app$ sam build
```

The SAM CLI builds a docker image from a Dockerfile and then installs dependencies defined in `hello_world/requirements.txt` inside the docker image. The processed template file is saved in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
sam-app$ sam local invoke HelloWorldFunction --event events/event.json
```

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
sam-app$ sam local start-api
sam-app$ curl http://localhost:3000/
```

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
      Events:
        HelloWorld:
          Type: Api
          Properties:
            Path: /hello
            Method: get
```

## Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
sam-app$ sam logs -n HelloWorldFunction --stack-name sam-app --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Unit tests

Tests are defined in the `tests` folder in this project. Use PIP to install the [pytest](https://docs.pytest.org/en/latest/) and run unit tests from your local machine.

```bash
sam-app$ pip install pytest pytest-mock --user
sam-app$ python -m pytest tests/ -v
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name sam-app
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
