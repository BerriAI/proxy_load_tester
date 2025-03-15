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

PASSING_MEDIAN_RESPONSE=150 # Expected 150ms for 20 RPS
PASSING_AVERAGE_RESPONSE=160

PASSING_AVERAGE_RESPONSE_LARGE_TESTS=300 # Expected 300ms for 100 RPS
PASSING_MEDIAN_RESPONSE_LARGE_TESTS=300

PASSING_FAILURE_COUNT=10
PASSING_NUMBER_REQUESTS=144             # Total number mins = 144 * 5 = 720 = 12 hours
PASSING_NUMBER_REQUESTS_DEV=15          # Total number mins = 12 * 5 = 60 = 1 hours


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

    

def get_current_litellm_version(proxy_endpoint: str):
    try:
        print(f"getting current litellm version from {proxy_endpoint}")
        response = requests.get(f'{proxy_endpoint}/health/readiness')
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


def calculate_aggregate_metrics(current_version):
    total_request_count = 0
    total_failure_count = 0
    average_response_times = []
    median_response_times = []
    total_regular_tests = 0


    large_total_request_count = 0
    large_total_failure_count = 0
    large_average_response_times = []
    large_median_response_times = []
    large_total_tests = 0

    file_name = f"all_results_{current_version}.csv"

    with open(file_name, newline="") as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            if "large" in row["Test-Name"]:
                large_total_request_count += int(row["Request Count"])
                large_total_failure_count += int(row["Failure Count"])
                large_median_response_times.append(float(row["Median Response Time"]))  
                large_average_response_times.append(float(row["Average Response Time"]))
                large_total_tests += 1
            else:
                total_request_count += int(row["Request Count"])
                total_failure_count += int(row["Failure Count"])
                median_response_times.append(float(row["Median Response Time"]))  
                average_response_times.append(float(row["Average Response Time"]))
                total_regular_tests += 1
        
    
    # upload this file to s3
    upload_to_s3(file_name, "litellm-load-tests", f"all_results_{current_version}.csv")
    # Calculating aggregate metrics
    total_tests = csvreader.line_num - 1  # Excluding header
    print("Total tests: " + str(total_tests), "current version: " + current_version + "passing number requests: " + str(PASSING_NUMBER_REQUESTS_DEV))
    if total_tests == 0:
        return None  # No data found
    
    if total_tests < PASSING_NUMBER_REQUESTS_DEV:
        return None
    



    # Calculating average of average response times
    average_of_average_response_times = sum(average_response_times) / total_regular_tests

    # Median of median response times
    median_of_median_response_times = sorted(median_response_times)[total_regular_tests // 2]
    
    # Calculate large test metrics outside of conditionals
    average_of_average_response_times_large = sum(large_average_response_times) / large_total_tests if large_total_tests > 0 else 0
    median_of_median_response_times_large = sorted(large_median_response_times)[large_total_tests // 2] if large_total_tests > 0 else 0
    
    # Create a comprehensive stats message that can be reused
    stats_message = (
        f"Version={current_version}\n"
        f"Regular Tests (20 RPS):\n"
        f"- Median Response Time={median_of_median_response_times}ms (threshold: {PASSING_MEDIAN_RESPONSE}ms)\n"
        f"- Average Response Time={average_of_average_response_times}ms (threshold: {PASSING_AVERAGE_RESPONSE}ms)\n"
        f"- Failure Count={total_failure_count} (threshold: {PASSING_FAILURE_COUNT})\n"
        f"Large Tests (100 RPS):\n"
        f"- Median Response Time={median_of_median_response_times_large}ms (threshold: {PASSING_MEDIAN_RESPONSE_LARGE_TESTS}ms)\n"
        f"- Average Response Time={average_of_average_response_times_large}ms (threshold: {PASSING_AVERAGE_RESPONSE_LARGE_TESTS}ms)\n"
        f"- Failure Count={large_total_failure_count} (threshold: {PASSING_FAILURE_COUNT})"
    )
    
    # Check all conditions and send comprehensive stats for any failure
    if median_of_median_response_times > PASSING_MEDIAN_RESPONSE:
        send_slack_message(f"❌❌❌❌❌❌❌❌❌❌\nRelease is unstable - Regular Median Response Time exceeded\n{stats_message}")
        return False
    
    if total_failure_count > PASSING_FAILURE_COUNT:
        send_slack_message(f"❌❌❌❌❌❌❌❌❌❌\nRelease is unstable - Regular Failure Count exceeded\n{stats_message}")
        return False

    if average_of_average_response_times > PASSING_AVERAGE_RESPONSE:
        send_slack_message(f"❌❌❌❌❌❌❌❌❌❌❌\nRelease is unstable - Regular Average Response Time exceeded\n{stats_message}")
        return False
    
    ## Check for large tests
    if large_total_failure_count > PASSING_FAILURE_COUNT:
        send_slack_message(f"❌❌❌❌❌❌❌❌❌❌\nRelease is unstable - Large Test Failure Count exceeded\n{stats_message}")
        return False
    
    if average_of_average_response_times_large > PASSING_AVERAGE_RESPONSE_LARGE_TESTS:
        send_slack_message(f"❌❌❌❌❌❌❌❌❌❌❌\nRelease is unstable - Large Test Average Response Time exceeded\n{stats_message}")
        return False
    
    if median_of_median_response_times_large > PASSING_MEDIAN_RESPONSE_LARGE_TESTS:
        send_slack_message(f"❌❌❌❌❌❌❌❌❌❌❌\nRelease is unstable - Large Test Median Response Time exceeded\n{stats_message}")
        return False
    
    # If all tests pass, send success message with all stats
    send_slack_message(f"✅✅✅✅✅✅✅✅✅✅\nRelease is stable\n{stats_message}")

    return {
        "Request Count": total_request_count,
        "Failure Count": total_failure_count,
        "Median Response Time": median_of_median_response_times,
        "Average Response Time": average_of_average_response_times
    }




def write_test_results_to_csv(csv_file, current_version, test_name=None):
    print("writing test results for file: " + csv_file + "for current version: " + current_version + "for test name: " + test_name)
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
        
        send_slack_message(
            message=f"Test results for {current_version} \n {results}"

        )
    return
            
