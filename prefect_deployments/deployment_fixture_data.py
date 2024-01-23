from prefect import flow

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/felixlattmann/bundesliga_dashboard.git",
        entrypoint="etl/s3/get_fixtures.py:check_current_round_for_changes",
    ).deploy(
        name="fixtures-deployment",
        work_pool_name="container-workpool",
        schedule={"timezone": "Europe/Berlin", "cron": "0 5 * * *"},
    )
