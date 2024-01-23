from dotenv import load_dotenv
from os.path import abspath, join, dirname
from prefect_aws import AwsCredentials
from os import environ


def load_env():
    env_path = abspath(join(dirname(__file__), "../..", ".env"))
    load_dotenv(env_path)


def authenticate_aws() -> AwsCredentials:
    return AwsCredentials.load("aws-login")
