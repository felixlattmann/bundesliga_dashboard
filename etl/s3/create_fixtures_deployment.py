import sys
from standard_functions import load_env
from get_fixtures import check_current_round_for_changes


load_env()


if __name__ == "__main__":
    check_current_round_for_changes.serve(
        name="Deployment for fixture pipelines",
        tags=["fixtures", "bundesliga"],
        schedule={
            "cron": "0 5 * * *",
            "timezone": "Europe/Berlin",
        },
    )
