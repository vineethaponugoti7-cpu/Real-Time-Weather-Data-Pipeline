"""
AWS version — Lambda consumer.

This function is triggered by the Kinesis stream. For each record, it decodes
the weather JSON and writes it to an S3 bucket as a JSON object.

Deploy this as an AWS Lambda function with:
  - A Kinesis trigger on your weather stream.
  - An environment variable S3_BUCKET set to your target bucket.
  - An IAM role allowing kinesis:GetRecords and s3:PutObject.
"""

import base64
import json
import os
from datetime import datetime, timezone

import boto3

BUCKET_NAME = os.environ.get("S3_BUCKET")
if not BUCKET_NAME:
    raise ValueError("S3_BUCKET environment variable not set.")

s3 = boto3.client("s3")


def lambda_handler(event, context):
    saved = 0
    for record in event["Records"]:
        try:
            payload = base64.b64decode(record["kinesis"]["data"])
            data = json.loads(payload)

            safe_city = str(data.get("city", "unknown")).replace(" ", "_")
            key = f"weather/{safe_city}_{datetime.now(timezone.utc).isoformat()}.json"

            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=key,
                Body=json.dumps(data),
                ContentType="application/json",
            )
            saved += 1
            print(f"Saved to S3: {key}")

        except Exception as exc:  # noqa: BLE001
            print(f"Error processing record: {exc}")

    return {
        "statusCode": 200,
        "body": json.dumps(f"Processed {saved} record(s) to S3."),
    }
