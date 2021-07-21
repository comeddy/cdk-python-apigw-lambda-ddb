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