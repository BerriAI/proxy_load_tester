import subprocess
import traceback

def run_locust_test(script_name):
    try:
        command = [
            "locust",
            "-f", script_name,
            "--headless",
            "-u", "20",
            "-r", "20",
            "-H", "https://staging.litellm.ai/",
            "-t", "100",
            "--csv", "load_test"
        ]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(e)
        print(traceback.format_exc())
    except Exception as e:
        print(e)
        print(traceback.format_exc())

def run_failed_responses_chat_completion():
    run_locust_test("failed_responses.py")

def run_all_cache_hits_locust_test():
    run_locust_test("all_cache_hits.py")

def run_no_cache_hits_locust_test():
    run_locust_test("no_cache_hits.py")

def run_cache_off_locust_test():
    run_locust_test("no_cache.py")