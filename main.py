"""
Fast API app

- POST /start/load/test, params = {version, commit_hash}
"""
import time
from typing import Optional
from fastapi import FastAPI, Query, BackgroundTasks
from should_run_test import bump_version_and_check_num_models
from github_helper import new_stable_release
from run_locust_tests import run_all_cache_hits_locust_test, run_cache_off_locust_test, run_failed_responses_chat_completion, run_locust_test, run_no_cache_hits_locust_test
from interpret_load_test import write_test_results_to_csv, get_current_litellm_version, calculate_aggregate_metrics

app = FastAPI()
def background_task(version: str, commit_hash: str, skip_sleep: Optional[bool] = False):
    print(f"Starting load test for version {version} with commit hash {commit_hash}")

    # it takes 15 mins for a new docker build, sleep for 30 mins
    if skip_sleep is True:
        print("skipping sleep")
    else:
        time.sleep(30*60)

    # bump staging server version
    bump_version_and_check_num_models()
    
    # get current litellm version
    current_version = get_current_litellm_version()
    csv_file = "load_test_stats.csv"

    print(f"current_version={current_version}, testing version={version}")
    if current_version != version:
        print(f"version mismatch, skipping test. Current version={current_version}, version={version}. Not running stable tests and not making a new release")
        return

    # run stable release testing
    run_stable_release_testing(
        current_version=current_version,
        csv_file=csv_file
    )
    print(f"testing done, making new stable release, version={version}, commit_hash={commit_hash}")

    if check_metrics_on_release(current_version, csv_file) is True:
        # new release
        new_stable_release(
            version=version,
            commit_hash=commit_hash
        )
    else:
        print("got an unstable release")

@app.post("/start/load/test")
async def start_load_test(
    background_tasks: BackgroundTasks,
    version: str = Query(..., description="Version of the load test"),
    commit_hash: str = Query(..., description="Commit hash for the load test"),
    skip_sleep: Optional[bool] = False
):

    print(f"Starting load test for version {version} with commit hash {commit_hash}")
    background_tasks.add_task(background_task, version, commit_hash, skip_sleep)

    return {
        "message": "Load test started",
        "version": version,
        "commit_hash": commit_hash
    }

def run_stable_release_testing(current_version, csv_file):
    # runs this 4 times 
    # each test is 5 mins, 
    # total time = 60 mins for all tests
    for _ in range(4):
        run_all_cache_hits_locust_test()
        write_test_results_to_csv(
            csv_file=csv_file,
            current_version=current_version,
            test_name="all_cache_hits"
        )


        run_cache_off_locust_test() 
        write_test_results_to_csv(
            csv_file=csv_file,
            current_version=current_version,
            test_name="cache_off"
        )


        run_no_cache_hits_locust_test()
        write_test_results_to_csv(
            csv_file=csv_file,
            current_version=current_version,
            test_name="no_cache_hits"
        )


def check_metrics_on_release(current_version, csv_file):
    print("checking aggregate metrics on release")
    aggregate_metrics = calculate_aggregate_metrics(current_version)
    if aggregate_metrics is not None:
        if aggregate_metrics == False:
            # bad release
            return False
        else:
            return True
    return False


    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)