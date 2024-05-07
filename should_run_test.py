# decides if we need to run a load test or not

"""
When the load test is run:
New litellm release -> trigger a new staging deploy, start test
1. Get latest litellm version from github
2. Check if the latest version is in `stable_releases.txt` or `unstable_releases.txt`
3. If not -> start running tests
"""
STABLE_RELEASES_FILE = "stable_releases.txt"
UNSTABLE_RELEASES_FILE = "unstable_releases.txt"

# Function to load stable releases from file
def load_stable_releases():
    try:
        with open(STABLE_RELEASES_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

def load_unstable_releases():
    try:
        with open(UNSTABLE_RELEASES_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

import github_helper
import requests
import time
import os 
from dotenv import load_dotenv
load_dotenv()




def check_if_latest_was_tested():
    latest = github_helper.get_latest_relased_version()
    latest = str(latest)
    # remove the 'v' from the version
    latest = latest.replace("v", "")

    print("latest version from github", latest)
    if "dev" in latest or "stable" in latest:
        print("latest version is a dev or stable version, skipping load test")
        return False


    print("latest version: ", latest)

    _stable_releases = load_stable_releases()
    _unstable_releases = load_unstable_releases()
    print("_stable_releases: ", _stable_releases, "_unstable_releases: ", _unstable_releases)

    if latest in _stable_releases or latest in _unstable_releases:
        return True, latest
    else:
        print("latest was not tested")
        return False, latest


def get_current_litellm_version():
    try:
        print("getting current litellm version")
        response = requests.get('https://staging.litellm.ai/health/readiness')
        version = response.json()["litellm_version"]
        print("current litellm version on staging", version)
        return version
    except:
        pass



def should_run_test():
    was_latest_tested, latest = check_if_latest_was_tested()
    if not was_latest_tested:
        # we need to run load testing ! 
        # before running the test - check if we need to re-deploy staging
        version = get_current_litellm_version()
        if version != latest:
            # run curl to bump staging version
            _webhook = os.getenv('STAGING_DEPLOY_WEBHOOK')
            result = requests.get(_webhook)
            if result.status_code == 200:
                print("triggered new staging deploy + ready to run a new test. sleeping for 30 seconds before running a new test")
                time.sleep(30)
                return True
        return True
    else:
        print("no need to trigger new staging deploy / load test. check_if_latest_was_tested=True")
        return False



def main():
    while True:
        if should_run_test():
            # Run your test code here
            print("should_run_test = True. Running the load test")
            break
        else:
            print("Not running the test, should_run_test returned False. Sleeping for 1 min and then calling should_run_test again.")
            time.sleep(60)  # Wait for 1 minute

if __name__ == "__main__":
    main()