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