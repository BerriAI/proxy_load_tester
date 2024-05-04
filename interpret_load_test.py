import csv
import os
import requests
import dotenv
import time
import sys
import requests
import csv
import boto3
import github_helper

from dotenv import load_dotenv
load_dotenv()

PASSING_MEDIAN_RESPONSE=200
PASSING_AVERAGE_RESPONSE=200
PASSING_FAILURE_COUNT=10
PASSING_NUMBER_REQUESTS=144             # Total number mins = 144 * 5 = 720 = 12 hours
PASSING_NUMBER_REQUESTS_DEV=5    


STABLE_RELEASES_FILE = "stable_releases.txt"
UNSTABLE_RELEASES_FILE = "unstable_releases.txt"

# Function to load stable releases from file
def load_stable_releases():
    try:
        with open(STABLE_RELEASES_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to save stable releases to file
def save_stable_releases(stable_releases):
    with open(STABLE_RELEASES_FILE, "w") as file:
        file.write("\n".join(stable_releases))


def load_unstable_releases():
    try:
        with open(UNSTABLE_RELEASES_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

def save_unstable_releases(unstable_releases):
    with open(UNSTABLE_RELEASES_FILE, "w") as file:
        file.write("\n".join(unstable_releases))


import boto3

def upload_to_s3(file_path, bucket_name, object_name):
    """
    Uploads a file to an S3 bucket.

    :param file_path: Path to the file to upload.
    :param bucket_name: Name of the S3 bucket.
    :param object_name: S3 object name (the key under which the file will be stored in the bucket).
    :return: True if the file was uploaded successfully, False otherwise.
    """
    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        # Upload the file
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"File uploaded successfully to bucket '{bucket_name}' with key '{object_name}'")
        return True
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return False

# each row is is a test that runs 5 mins 
# load test runs for 12 hours

    

def get_current_litellm_version():
    try:
        print("getting current litellm version")
        response = requests.get('https://staging.litellm.ai/health/readiness')
        version = response.json()["litellm_version"]
        
        filename = f"all_results_{version}.csv"
        # create a new file if it does not exist
        if not os.path.isfile(filename):
            open(filename, "w").close()
        return version
    except:
        pass


def send_slack_message(message):
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", None)
    if slack_webhook_url is None:
        raise Exception("Missing SLACK_WEBHOOK_URL from environment")

    payload = {"text": message}
    headers = {"Content-type": "application/json"}
    print("Slack Alert: " + message)

    response = requests.post(slack_webhook_url, json=payload, headers=headers)

    if response.status_code == 200:
        pass


def calculate_aggregate_metrics(file_name, current_version):
    total_request_count = 0
    total_failure_count = 0
    average_response_times = []
    median_response_times = []

    with open(file_name, newline="") as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            total_request_count += int(row["Request Count"])
            total_failure_count += int(row["Failure Count"])
            median_response_times.append(float(row["Median Response Time"]))  
            average_response_times.append(float(row["Average Response Time"]))
    # upload this file to s3
    upload_to_s3(file_name, "litellm-load-tests", f"all_results_{current_version}.csv")
    # Calculating aggregate metrics
    total_tests = csvreader.line_num - 1  # Excluding header
    print("Total tests: " + str(total_tests), "current version: " + current_version)
    if total_tests == 0:
        return None  # No data found
    
    if total_tests < PASSING_NUMBER_REQUESTS_DEV:
        return None
    



    # Calculating average of average response times
    average_of_average_response_times = sum(average_response_times) / total_tests

    # Median of median response times
    median_of_median_response_times = sorted(median_response_times)[total_tests // 2]
    if median_of_median_response_times > PASSING_MEDIAN_RESPONSE:
        # send a slack alert 
        send_slack_message(f"❌❌❌❌❌❌❌❌❌❌\nRelease is unstable. \nVersion={current_version} \n Median Response Time={median_of_median_response_times} is greater than {PASSING_MEDIAN_RESPONSE}")
        return False
    
    if total_failure_count > PASSING_FAILURE_COUNT:
        # send a slack alert

        send_slack_message(f"❌❌❌❌❌❌❌❌❌❌\nRelease is unstable. \nVersion={current_version} \n Failure Count={total_failure_count} is greater than {PASSING_FAILURE_COUNT}")
        return False

    if average_of_average_response_times > PASSING_AVERAGE_RESPONSE:
        send_slack_message(f"❌❌❌❌❌❌❌❌❌❌❌\nRelease is unstable. \nVersion={current_version} \n Average Response Time={average_of_average_response_times} is greater than {PASSING_AVERAGE_RESPONSE}")
        return False
    
    return {
        "Request Count": total_request_count,
        "Failure Count": total_failure_count,
        "Median Response Time": median_of_median_response_times,
        "Average Response Time": average_of_average_response_times
    }




def interpret_results(csv_file, current_version, test_name=None):
    with open(csv_file, newline="") as csvfile:
        csvreader = csv.DictReader(csvfile)
        rows = list(csvreader)
        """
        in this csv reader
        - Create 1 new column "Status"
        - if a row has a median response time < 300 and an average response time < 300, Status = "Passed ✅"
        - if a row has a median response time >= 300 or an average response time >= 300, Status = "Failed ❌"
        - Order the table in this order Name, Status, Median Response Time, Average Response Time, Requests/s,Failures/s, Min Response Time, Max Response Time, all other columns
        """

        # Add a new column "Status"

        for row in rows:
            median_response_time = float(
                row["Median Response Time"].strip().rstrip("ms")
            )
            average_response_time = float(
                row["Average Response Time"].strip().rstrip("s")
            )

            row["Test-Name"] = test_name

            request_count = int(row["Request Count"])
            failure_count = int(row["Failure Count"])

            failure_percent = round((failure_count / request_count) * 100, 2)

            # Determine status based on conditions
            if (
                median_response_time < 150
                and average_response_time < 150
                and failure_percent < 5
            ):
                row["Status"] = "Passed ✅"
            else:
                row["Status"] = "Failed ❌"

        results = "\n"
        # Construct Markdown table rows
        for row in rows:
            name = row["Name"]
            status = row["Status"]
            median_response_time = row["Median Response Time"]
            average_response_time = row["Average Response Time"]
            requests_per_second = row["Requests/s"]
            failures_per_second = row["Failures/s"]
            request_count = row["Request Count"]
            failure_count = row["Failure Count"]

            result = f"""
                Current Time: {time.strftime("%m-%d %H:%M:%S")}
                Name: {name}
                Status: {status}    
                Median Response Time: {median_response_time}
                Average Response Time: {average_response_time}
                Requests/s: {requests_per_second}
                Failures/s: {failures_per_second}
                Request Count: {request_count}
                Failure Count: {failure_count}
            \n\n    
            """

            results += result

        # Stable Release Logic ######
        stable_releases = load_stable_releases()
        print("stable releases", stable_releases)

        unstable_releases = load_unstable_releases()
        print("unstable releases", unstable_releases)

        print("current version", current_version)
        if current_version in stable_releases:
            return results

        if current_version in unstable_releases:
            return results

        file_name = f"all_results_{current_version}.csv"
        with open(file_name, "a", newline="") as csvfile:
            # add all the rows to the csv file
            # remove the row if "Name" == "Aggregated"
            rows = [row for row in rows if row["Name"] != "Aggregated"]
            rows = [row for row in rows if row["Test-Name"] != "simple_openai_proxy"]

            writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())

            # only write the header if the file is empty

            if os.stat(file_name).st_size == 0:
                writer.writeheader()

            writer.writerows(rows)
            

        # Check if we have enough rows to create a new litellm release
        # Read CSV FILE and count total number of entries  
        aggregate_metrics = calculate_aggregate_metrics(file_name, current_version)
        if aggregate_metrics is not None:
            if aggregate_metrics == False:
                # it failed a test - this is an unstable release
                unstable_releases.append(current_version)
                return results
            
            stable_releases.append(current_version)
            send_slack_message(f"✅Release is stable. \n`Version={current_version}` \n `{aggregate_metrics}`")

            # queue a new stable release on github
            github_helper.new_stable_release(version=current_version)
        save_stable_releases(stable_releases)
        save_unstable_releases(unstable_releases)
        return results


if __name__ == "__main__":
    print("interpreting load test results")
    version = get_current_litellm_version()
    print("current litellm version", version)
    if len(sys.argv) < 2:
        print("Usage: python3 interpret_load_test.py <test_name>")
        sys.exit(1)

    test_name = sys.argv[1]
    print("Interpreting results for test: " + test_name)
    csv_file = "load_test_stats.csv"  # Change this to the path of your CSV file
    markdown_table = interpret_results(
        csv_file, 
        current_version=version,
        test_name=test_name
    )
    print(markdown_table)
    markdown_table = "\nTest Name: " + f"`{test_name}`\n" + markdown_table


    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", None)
    if slack_webhook_url is None:
        raise Exception("Missing SLACK_WEBHOOK_URL from environment")
    
    payload = {"text": markdown_table}
    headers = {"Content-type": "application/json"}


    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", None)
    if slack_webhook_url is None:
        raise Exception("Missing SLACK_WEBHOOK_URL from environment")

    payload = {"text": markdown_table}
    headers = {"Content-type": "application/json"}

    response = requests.post(slack_webhook_url, json=payload, headers=headers)

    if response.status_code == 200:
        pass
    else:
        print("sending slack message failed")
        print(response.text)
