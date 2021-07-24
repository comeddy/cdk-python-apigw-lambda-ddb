
# Introduction
CDK를 이용해 API Gateway, Lambda, DynamoDB를 생성해봅니다. 


# Prerequisites
AWS Cloud9을 원하는 리전(e.g., us-east-1, ap-northeast-2 등)에 구성한후, aws-cdk를 최신버전으로 설치합니다.(option --force)

- Sign in to the [AWS Management Console](https://console.aws.amazon.com/)
- Go to [Cloud9](https://console.aws.amazon.com/cloud9/) environment. and Click Open IDE
```
$ npm install -g aws-cdk --force
```

설치된 CDK 버전을 확인합니다.
```
$ cdk --version
```
$ cdk --version 
1.115.0 (build 7e41b6b)

## Project creation

CDK 작업디렉토리 생성합니다.

```
$ mkdir cdk
$ cd cdk
```

CDK 명령어를 이용해서 python 프로젝트를 만들어봅니다.

```
$ cdk init --language=python
```
Applying project template app for python

# Welcome to your CDK Python project!

This is a blank project for Python development with CDK.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

## Add module

Setup.py에 필요한 모듈을 추가합니다.
apigateway, lambda, dynamodb를 함께 추가합니다.

```python
    install_requires=[
        "aws-cdk.core==1.115.0",
        "aws-cdk.aws-apigateway",
        "aws-cdk.aws-lambda",
        "aws-cdk.aws-dynamodb"
    ],
```

Once the virtualenv is activated, you can install the required dependencies.
To add additional dependencies, for example other CDK libraries, just add them to your setup.py file and rerun the pip install -r requirements.txt command.

```
$ pip install -r requirements.txt
```

# Lambda code

디렉토리를 만들고 그 아래 다음 코드를 작성합니다.

```
$ mkdir lambda
$ touch lambda/app.py
```

lambda/app.py 코드를 작성합니다.

```python
import json
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    try:
        event_body = json.loads(event["body"])
        if "local" in event_body and event_body["local"] == True:
            dynamodb = boto3.resource("dynamodb", endpoint_url="http://dynamodb:8000")
        else:
            dynamodb = boto3.resource("dynamodb")

        table = dynamodb.Table("Demo")
        table.put_item(
            Item={
                "Key": event_body["key"],
                "CreateDate": datetime.utcnow().isoformat()
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "succeeded",
            }),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": e.args
            }),
    }
```

# Deployment & Provisioning code creation

프로젝트 root 디렉토리 app.py을 다음과 같이 변경합니다.
lambda 

```python
#!/usr/bin/env python3

from aws_cdk import (
    aws_apigateway,
    aws_lambda,
    aws_dynamodb,
    core
)

from aws_cdk.aws_dynamodb import (
    Table,
    Attribute,
    AttributeType
)

class LambdaSampleStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        handler = aws_lambda.Function(
            self, "backend",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="app.lambda_handler",
            code=aws_lambda.AssetCode(path="./lambda"))

        api = aws_apigateway.LambdaRestApi(self, "SampleLambda", handler=handler, proxy=False)
        api.root.add_resource("ddb").add_method("POST")

        table = Table(
            self, "ItemsTable",
            table_name="Demo",
            partition_key=Attribute(
                name="Key",
                type=AttributeType.STRING
            ),
            sort_key=Attribute(
                name="CreateDate",
                type=AttributeType.STRING
            )
        )
        table.grant_write_data(handler)

app = core.App()
LambdaSampleStack(app, "LambdaSampleStack")

app.synth()
```


# Ready to deploy

```
$ cdk bootstrap
```
 ⏳  Bootstrapping environment aws://************/us-east-1...
 ✅  Environment aws://*************/us-east-1 bootstrapped (no changes).

# Deploy

Synthesize (cdk synth) or deploy (cdk deploy) the example
```
$ cdk deploy
```

# Tests

Sample Lambda endpoint의 resource 'ddb'에 POST로 요청후, DynamoDB Table Demo과 Items를 확인해봅니다.
```shell
$ curl -X POST -H "Content-Type: application/json" -d '{"key": "demo-data"}' https://**********.execute-api.us-east-1.amazonaws.com/prod/ddb
{"message": "succeeded"}
```



## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
