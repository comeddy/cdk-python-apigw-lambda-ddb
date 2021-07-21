
# Introduction
CDK를 이용해 API Gateway, Lambda, DynamoDB를 생성합니다. 


# Prerequisites

aws-cdk 를 최신버전으로 설치합니다. 

```
$ npm install -g aws-cdk --force
```
버전을 확인합니다.
```
$ cdk --version
```

CDK 작업디렉토리 생성합니다.

```
$ mkdir cdk
$ cd cdk
```

CDK 명령어를 이용해서 프로젝트를 만들어봅니다.

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

## 모듈 추가

Setup.py에 필요한 모듈을 추가합니다.
apigateway, lambda, dynamodb를 함께 추가합니다.

```
    install_requires=[
        "aws-cdk.core==1.114.0",
        "aws-cdk.aws-apigateway",
        "aws-cdk.aws-lambda",
        "aws-cdk.aws-dynamodb"
    ],
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
