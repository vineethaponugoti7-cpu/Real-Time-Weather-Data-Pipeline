"""
AWS version — Kinesis producer.

Fetches weather for each city and streams it to an AWS Kinesis Data Stream.
A Lambda function (see lambda_consumer.py) reads from the stream and writes
each record to S3.

This is the cloud deployment of the pipeline. To run it you need AWS
credentials configured and a Kinesis stream created. For a version that runs
with no AWS setup, use src/pipeline_local.py instead.

Run:
    python aws/kinesis_producer.py
"""

import json
import sys
import time
from pathlib import Path

import boto3

# Allow importing the shared modules from ../src
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import config          # noqa: E402
from weather import fetch_weather  # noqa: E402

kinesis = boto3.client("kinesis", region_name=config.AWS_REGION)


def put_to_kinesis(record: dict) -> None:
    """Send a single JSON record to the Kinesis stream."""
    kinesis.put_record(
        StreamName=config.KINESIS_STREAM,
        Data=json.dumps(record).encode("utf-8"),
        PartitionKey=record["city"],
    )
    ts = record["timestamp"].replace("T", " ").split(".")[0]
    print(f"{record['city']:<15} | {record['temp']:5.1f}C | {ts}")


def main() -> None:
    if not config.OWM_API_KEY:
        print("[FATAL] OWM_API_KEY is not set. See setup.env.example.")
        return

    print("Kinesis producer started. Press Ctrl-C to stop.\n")
    try:
        while True:
            for city in config.CITIES:
                record = fetch_weather(city)
                if record:
                    put_to_kinesis(record)
            time.sleep(config.POLL_INTERVAL_SEC)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
