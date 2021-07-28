#!/usr/bin/env python3

from aws_cdk import (
    aws_apigateway as _apigw,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
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
        
        # create lambda function
        handler = _lambda.Function(
            self, "backend",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="handler.lambda_handler",
            code=_lambda.AssetCode(path="./lambda"))
        
        # define the API endpoint and associate the handler
        base_api = _apigw.LambdaRestApi(self, "SampleLambda", handler=handler, proxy=False)
        base_api.root.add_resource("ddb").add_method("POST")

        # create dynamo table
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
        
        # grant permission to lambda to write from demo table
        table.grant_write_data(handler)

app = core.App()
LambdaSampleStack(app, "LambdaSampleStack")

app.synth()
