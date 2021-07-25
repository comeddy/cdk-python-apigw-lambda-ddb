
# Introduction
본 실습은 애플리케이션을 개발하기 위하여 CDK를 이용하여 Python언어로 인프라 및 개발 소스를 배포하는 방법을 살펴 봅니다.<br>
차례대로 Lambda, DynamoDB 그리고 API Gateway를 작성해봅니다.
- Local DynamoDB와 Amazon DynamoDB 각각 개발버전과 운영버전으로 선택가능합니다.   

# Prerequisites
AWS Cloud9을 원하는 리전(e.g., us-east-1, ap-northeast-2 등)에 구성한 후, aws-cdk를 최신버전으로 설치합니다.<br>
최신버전을 설치를 추천합니다.(강제옵션이 필요한 경우 option --force)

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

# Project creation

CDK 작업디렉토리 생성합니다.

```
$ mkdir cdk
$ cd cdk
```

CDK init 명령어를 이용해서 python 프로젝트를 만들어봅니다.

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

MacOS 및 Linux에서 virtualenv를 수동으로 생성하려면 아래와같이 실행합니다.

```
$ python3 -m venv .venv
```

초기화 프로세스가 완료되고 virtualenv가 생성되면 다음 단계를 사용하여 virtualenv를 활성화할 수 있습니다.

```
$ source .venv/bin/activate
```

Windows 플랫폼인 경우 다음과 같이 virtualenv를 활성화합니다.

```
% .venv\Scripts\activate.bat
```

# Add module

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

virtualenv가 활성화되면 필요한 종속성을 설치할 수 있습니다. <br>
다른 CDK 라이브러리와 같은 추가 종속성을 추가하려면 setup.py 파일에 추가하고 pip install -r requirements.txt 명령을 다시 실행하기만 하면 됩니다.

```
$ pip install -r requirements.txt
```

# Ready to deploy
CDK Toolkit Stack을 S3에 만들기 위하여 bootstrap을 합니다. 한번만 실행해주면 됩니다.

```
$ cdk bootstrap
```
 ⏳  Bootstrapping environment aws://123456789012/us-east-1...<br>
 ✅  Environment aws://123456789012/us-east-1 bootstrapped (no changes).


# Lambda code

디렉토리를 만들고 아래 다음 코드를 작성합니다.

```
$ mkdir lambda
$ touch lambda/handler.py
```

lambda/handler.py 코드를 작성합니다.

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

프로젝트 root 디렉토리의 app.py을 아래와 같이 변경합니다.

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
            handler="handler.lambda_handler",
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


# Deploy

Synthesize (cdk synth) or deploy (cdk deploy) the example
```
$ cdk deploy
```

# Testing the app

Sample Lambda endpoint의 resource 'ddb'에 POST로 요청후, DynamoDB Table Demo과 Items를 확인해봅니다.
```shell
$ curl -X POST -H "Content-Type: application/json" -d '{"key": "demo-data"}' https://**********.execute-api.us-east-1.amazonaws.com/prod/ddb
{"message": "succeeded"}
```

정리하려면 다음 명령을 실행합니다(DynamoDB 테이블, CloudWatch 로그 또는 S3 버킷은 제거되지 않습니다. 수동으로 수행해야 함).
```
$ cdk destroy
```

To exit the virtualenv python environment:
```
$ deactivate
```


## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!

This code has been tested and verified to run with AWS CDK 1.115.0 (build 7e41b6b)


