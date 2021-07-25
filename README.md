
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
        "aws-cdk.aws-dynamodb",
        "boto3"
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

# Local Lambda & DynamoDB Testing
로컬 머신에서 실행할 수 있는 단일 Lambda 함수가 있는 간단한 CDK 스택이 있다고 상상해 보십시오.<br>
로컬에서 CDK로 빌드된 Lambda 함수를 실행하려면 어떻게 해야 합니까?<br>
AWS에 Deploy하기전에 로컬에서 Lambda함수를 테스트하기 위한 DynamoDB의 환경을 만들어봅니다.<br>
Sam을 이용한 local DynamoDB 테스트를 패스할경우, 아래 Deploy to AWS로 이동합니다. <br>

## Table define

```
mkdir ddb
touch ddb/model.json
```
ddb 디렉토리를 만들고, 테이블 구조를 json 파일형식으로 작성합니다.

```json
{
  "TableName": "Demo",
  "KeySchema": [
    {
      "AttributeName": "Key",
      "KeyType": "HASH"
    },
    {
      "AttributeName": "CreateDate",
      "KeyType": "RANGE"
    }
  ],
  "AttributeDefinitions": [
    {
      "AttributeName": "Key",
      "AttributeType": "S"
    },
    {
      "AttributeName": "CreateDate",
      "AttributeType": "S"
    }
  ],
  "ProvisionedThroughput": {
    "ReadCapacityUnits": 5,
    "WriteCapacityUnits": 5
  }
}
```

## run DynamoDB-Local 
Docker 컨테이너에서 DynamoDB를 동작하도록 구성을 합니다.

```
$ docker pull amazon/dynamodb-local
```
```
sing default tag: latest
latest: Pulling from amazon/dynamodb-local
Digest: sha256:bdd26570dc0e0ae49e1ea9d49ff662a6a1afe9121dd25793dc40d02802e7e806
Status: Image is up to date for amazon/dynamodb-local:latest
docker.io/amazon/dynamodb-local:latest
```

```
$ docker network create ddb-network
$ docker network ls
```
network list를 확인해봅니다.
```
NETWORK ID     NAME          DRIVER    SCOPE
1f9367e4af57   bridge        bridge    local
045a3713c683   ddb-network   bridge    local
f6567b43ebd6   host          host      local
5b53f6defb87   none          null      local
```

```
$ docker run --network ddb-network --name dynamodb -p 8000:8000 amazon/dynamodb-local -jar DynamoDBLocal.jar -sharedDb

```
"Ctrl+C"로 컨테이너를 중지하고 

```
$ docker start dynamodb
```
을 실행하여 백그라운드에서 DynamoDB를 시작합니다.


## Add Table in DynamoDB-Local
현재 로컬 DynamoDB에는 테이블이 없기 때문에 앞서 정의한 'ddb/model.json'에 정의된 내용으로 테이블을 생성합니다.
```
$ aws dynamodb create-table --cli-input-json file://./ddb/model.json --endpoint-url http://localhost:8000

```
이제 로컬 DynamoDB 테이블이 생성되었습니다.

## Run Lambda-Local 
먼저 CloudFormation 템플릿을 생성하고 template.yaml 파일로 저장합니다.<br>
cdk를 local에서 실행하기위해 sam 명령어를 실행하는데, 이때 template.yaml파일이 필요합니다.
```
cdk synth --no-staging > template.yaml
```

로컬 DynamoDB의 컨테이너와 통신하기 위해 '--docker-netork'옵션이 필요하게되므로 주의하십시오.
```
$ sam local start-api --docker-network ddb-network
```

Cloud9 터미널에서 curl 명령어로 'POST' 엑세스합니다.
```
$ curl -X POST -H "Content-Type: application/json" -d '{"key": "demo-data", "local": true}' http://127.0.0.1:3000/ddb
```

```
Mounting backendCBA98286 at http://127.0.0.1:3000/ddb [POST]
You can now browse to the above endpoints to invoke your functions. You do not need to restart/reload SAM CLI while working on your functions, changes will be reflected instantly/automatically. You only need to restart SAM CLI if you update your AWS SAM template
2021-07-25 16:09:58  * Running on http://127.0.0.1:3000/ (Press CTRL+C to quit)
Invoking handler.lambda_handler (python3.8)
Skip pulling image and use local one: amazon/aws-sam-cli-emulation-image-python3.8:rapid-1.19.0.

Mounting /home/ec2-user/environment/cdk/lambda as /var/task:ro,delegated inside runtime container
START RequestId: c85e7f2d-43b4-43d7-9a88-7780d89c5e22 Version: $LATEST
END RequestId: c85e7f2d-43b4-43d7-9a88-7780d89c5e22
REPORT RequestId: c85e7f2d-43b4-43d7-9a88-7780d89c5e22  Init Duration: 0.39 ms  Duration: 264.50 ms     Billed Duration: 300 ms Memory Size: 128 MB     Max Memory Used: 128 MB
No Content-Type given. Defaulting to 'application/json'.
2021-07-25 16:10:12 127.0.0.1 - - [25/Jul/2021 16:10:12] "POST /ddb HTTP/1.1" 200 -
```


실행결과가 표시되면 성공입니다.
```
{"message": "succeeded"}
```

## validation DB
실제로 데이터가 로컬 DynamoDB에 등록되어있는지 확인합니다.
```
$ aws dynamodb scan --table-name Demo --endpoint-url http://localhost:8000
```

```json
{
    "Count": 1, 
    "Items": [
        {
            "CreateDate": {
                "S": "2021-07-25T16:10:11.689717"
            }, 
            "Key": {
                "S": "demo-data"
            }
        }
    ], 
    "ScannedCount": 1, 
    "ConsumedCapacity": null
}
```

## Stop Lambda-local
Lambda 환경에서 'Ctrl+C'로 종료합니다.<br>
그리고 DynamoDB 내용은 다음 명령으로 종료합니다.

```
$ docker stop dynamodb
$ docker rm dynamodb
```


# Deploy to AWS

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


