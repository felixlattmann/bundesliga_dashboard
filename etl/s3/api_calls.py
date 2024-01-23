from prefect import task, get_run_logger, flow
import requests
from os import environ
import json
from standard_functions import load_env, authenticate_aws
from prefect_aws.s3 import s3_upload
import pandas as pd
from io import StringIO
from prefect.blocks.system import Secret

load_env()
api_key_rapid = Secret.load("rapid-api-key")
s3_bucket_name = Secret.load("s3-bucket-name")
headers = {
    "X-RapidAPI-Key": api_key_rapid,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
}


@task
def api_call_get_current_round() -> str:
    _logger = get_run_logger()
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/rounds"
    querystring = {
        "league": "78",
        "season": "2023",
        "current": "true",
    }
    response = requests.get(url, headers=headers, params=querystring)
    _logger.info("Current round: " + response.json()["response"][0])
    return response.json()["response"][0]


@task
def api_call_get_fixtures_for_current_round(current_round) -> requests.Response:
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {
        "league": "78",
        "season": "2023",
        "round": current_round,
        "timezone": "Europe/Berlin",
    }
    response = requests.get(url, headers=headers, params=querystring)
    return response


@flow
async def load_json_into_s3_bucket():
    credentials = authenticate_aws()
    async with open("temp.json", "rb") as file:
        key = await s3_upload(
            bucket=s3_bucket_name,
            key="temp.json",
            data=file.read(),
            aws_credentials=credentials,
        )


@flow
def s3_test():
    _logger = get_run_logger()
    credentials = authenticate_aws()
    with open("temp.json", "rb") as file:
        key = s3_upload(
            data=file.read(),
            bucket=s3_bucket_name,
            aws_credentials=credentials,
        )
    _logger.info(f"Successful upload with key: {key}")


@task
def s3_upload_df_to_bucket(df: pd.DataFrame):
    _logger = get_run_logger()
    credentials = authenticate_aws()
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)

    key = s3_upload(
        data=csv_buffer,
        bucket=s3_bucket_name,
        aws_credentials=credentials,
    )
    _logger.info(f"Upload of the df-file to s3bucket successful. Key: {key}")
