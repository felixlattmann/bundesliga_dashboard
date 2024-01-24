import requests
import json
from prefect_aws import AwsCredentials
from prefect_aws.s3 import s3_upload, S3Bucket
from io import BytesIO
from standard_functions import load_env, authenticate_aws
from prefect import flow, get_run_logger, task
import pandas as pd
from prefect.blocks.system import Secret
from api_calls import (
    api_call_get_current_round,
    api_call_get_fixtures_for_current_round,
)
from botocore.exceptions import ClientError


@flow
def main_flow():
    file_not_found = False
    logger = get_run_logger()
    s3_bucket = get_bucket_using_credentials(logger)
    current_round_from_s3 = download_current_round_to_bytesIO_transform_to_string(
        s3_bucket, logger, file_not_found
    )
    if isinstance(current_round_from_s3, str):
        current_round_from_api = api_call_get_current_round()
        if current_round_from_api != current_round_from_s3:
            upload_current_round_to_s3_bucket(s3_bucket, logger, current_round_from_api)

    if isinstance(current_round_from_s3, bool):
        current_round_from_api = api_call_get_current_round()
        logger.info("Current_round_from_api: " + current_round_from_api)
        upload_current_round_to_s3_bucket(s3_bucket, logger, current_round_from_api)


@task
def upload_current_round_to_s3_bucket(s3_bucket: S3Bucket, logger, current_round: str):
    try:
        buf = BytesIO(bytes(current_round, encoding="utf-8"))
        s3_bucket.upload_from_file_object(
            buf, "current_rounds_storage/current_round.txt"
        )
    except Exception as ex:
        logger.error("Could not upload data to s3. Error-Message: ", ex)


@task
def get_bucket_using_credentials(logger) -> S3Bucket:
    try:
        credentials = AwsCredentials.load("aws-login")
        bucket_name = Secret.load("s3-bucket-name")
        s3_bucket = S3Bucket(bucket_name=bucket_name.get(), credentials=credentials)
        return s3_bucket

    except Exception as ex:
        logger.error(f"Could not get s3_bucket. Error-Message: ", ex)


@task
def download_current_round_to_bytesIO_transform_to_string(
    s3_bucket: S3Bucket, logger, file_not_found: bool
) -> str:
    try:
        buffer = BytesIO()
        s3_path = "current_rounds_storage/current_round.txt"
        s3_bucket.download_object_to_file_object(s3_path, buffer)
        current_round_from_s3 = buffer.read().decode("utf-8")
        return current_round_from_s3

    except ClientError as ex:
        logger.info("File was not found in s3_bucket. Skipping equality check.")
        return True

    except Exception as ex:
        logger.error(f"Could not download object from s3. Error-Message: ", str(ex))


if __name__ == "__main__":
    main_flow()
