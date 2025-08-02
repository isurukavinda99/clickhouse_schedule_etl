import boto3
import requests
import os
from datetime import datetime
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # ClickHouse configuration
    CLICKHOUSE_HOST = os.environ['CLICKHOUSE_HOST']
    CLICKHOUSE_PORT = os.environ.get('CLICKHOUSE_PORT', 8123)
    CLICKHOUSE_USER = os.environ['CLICKHOUSE_USER']
    CLICKHOUSE_PASSWORD = os.environ['CLICKHOUSE_PASSWORD']
    CLICKHOUSE_DB = os.environ['CLICKHOUSE_DB']
    CLICKHOUSE_TABLE = os.environ['CLICKHOUSE_TABLE']

    # S3 configuration
    S3_BUCKET = os.environ['S3_BUCKET']
    S3_KEY = f"{CLICKHOUSE_TABLE}.csv"

    query = f"SELECT * FROM {CLICKHOUSE_DB}.{CLICKHOUSE_TABLE} FORMAT CSVWithNames"

    try:
        response = requests.post(
            f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
            data=query,
            auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD)
        )

        if response.status_code == 200:
            s3 = boto3.client('s3')

            # Check if the file already exists
            try:
                s3.head_object(Bucket=S3_BUCKET, Key=S3_KEY)
                # If it exists, rename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archived_key = f"{CLICKHOUSE_TABLE}_{timestamp}.csv"

                s3.copy_object(
                    Bucket=S3_BUCKET,
                    CopySource={'Bucket': S3_BUCKET, 'Key': S3_KEY},
                    Key=archived_key
                )
                s3.delete_object(Bucket=S3_BUCKET, Key=S3_KEY)
                print(f"Existing file renamed to {archived_key}")

            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    print("No existing file found. Proceeding to upload new file.")
                else:
                    print("Error checking existing file:")
                    print(e.response['Error']['Code'], "-", e.response['Error']['Message'])
                    return

            # Upload new file
            try:
                s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=response.content)
                print(f"New data exported to S3 as {S3_KEY}")
            except Exception as e:
                print("Unexpected error during S3 upload:")
                print(str(e))

        else:
            print(f"ClickHouse export failed: {response.text}")

    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    lambda_handler({}, None)
