import requests
import json
from prefect_aws.s3 import s3_upload
from io import BytesIO
from standard_functions import load_env, authenticate_aws
from prefect import flow, get_run_logger, task
import pandas as pd
from os import environ
from api_calls import (
    api_call_get_current_round,
    api_call_get_fixtures_for_current_round,
    s3_upload_df_to_bucket,
)

# Load .env
load_env()
old_current_round = None


# classes
class FixtureData:
    def __init__(
        self,
        dateandtime,
        home,
        away,
        venue,
        home_goals,
        away_goals,
        home_logo_url,
        away_logo_url,
    ):
        self.dateandtime = dateandtime
        self.home_team = home
        self.away_team = away
        self.venue = venue
        self.home_goals = home_goals
        self.away_goals = away_goals
        self.home_logo_url = home_logo_url
        self.away_logo_url = away_logo_url


# flow
@flow
def check_current_round_for_changes():
    _logger = get_run_logger()
    global old_current_round
    current_round = api_call_get_current_round()

    if old_current_round is None:
        old_current_round = current_round
        res = api_call_get_fixtures_for_current_round(current_round)
        df = transform_fixtures_response_to_df(res)
        credentials = authenticate_aws()
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer)
        key = s3_upload(
            data=csv_buffer.read(),
            bucket=environ["S3_BUCKET_NAME"],
            aws_credentials=credentials,
            key="fixture_data_from_current_round.csv",
        )
        _logger.info(f"Upload of the df-file to s3bucket successful. Key: {key}")

    elif old_current_round != current_round:
        api_call_get_fixtures_for_current_round(current_round)
        df = transform_fixtures_response_to_df(res)
        credentials = authenticate_aws()
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer)
        key = s3_upload(
            data=csv_buffer.read(),
            bucket=environ["S3_BUCKET_NAME"],
            aws_credentials=credentials,
            key="fixture_data_from_current_round.csv",
        )
        _logger.info(f"Upload of the df-file to s3bucket successful. Key: {key}")

    else:
        _logger.info(
            f"Rounds did not change. No api-call to fetch fixtures neccessary. old_round: {old_current_round}, new_round: {current_round}"
        )


# etl functions
@task
def transform_fixtures_response_to_df(res: requests.Response) -> pd.DataFrame:
    fixture_data_list = []
    json_object = res.json()
    for entry in json_object["response"]:
        dateandtime = entry["fixture"]["date"]
        home = entry["teams"]["home"]["name"]
        away = entry["teams"]["away"]["name"]
        venue = entry["fixture"]["venue"]["name"]
        home_goals = entry["goals"]["home"]
        away_goals = entry["goals"]["away"]
        home_logo_url = entry["teams"]["home"]["logo"]
        away_logo_url = entry["teams"]["away"]["logo"]
        fix = FixtureData(
            dateandtime,
            home,
            away,
            venue,
            home_goals,
            away_goals,
            home_logo_url,
            away_logo_url,
        )
        fixture_data_list.append(fix)

    dateandtime = [entry.dateandtime for entry in fixture_data_list]
    home_team = [entry.home_team for entry in fixture_data_list]
    away_team = [entry.away_team for entry in fixture_data_list]
    venue = [entry.venue for entry in fixture_data_list]
    home_goals = [entry.home_goals for entry in fixture_data_list]
    away_goals = [entry.away_goals for entry in fixture_data_list]
    home_logo_url = [entry.home_logo_url for entry in fixture_data_list]
    away_logo_url = [entry.away_logo_url for entry in fixture_data_list]

    dict_ = {
        "dateandtime": dateandtime,
        "home_team": home_team,
        "away_team": away_team,
        "venue": venue,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "home_logo_url": home_logo_url,
        "away_logo_url": away_logo_url,
    }

    df = pd.DataFrame(dict_)
    return df


def save_response_to_temp_file(response):
    with open("temp.json", "w") as outfile:
        json.dump(response.json(), outfile, indent=2)


def test_transform():
    with open("temp.json", "r") as file:
        json_object = json.load(file)

    print(json_object["fixture"])


check_current_round_for_changes()
