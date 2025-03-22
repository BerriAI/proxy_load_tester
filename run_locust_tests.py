import subprocess
import traceback

def run_locust_test(script_name, proxy_endpoint: str):
    try:
        command = [
            "locust",
            "-f", script_name,
            "--headless",
            "-u", "20",
            "-r", "20",
            "-H", f"{proxy_endpoint}/",
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

def run_failed_responses_chat_completion(proxy_endpoint: str):
    run_locust_test("failed_responses.py", proxy_endpoint)

def run_all_cache_hits_locust_test(proxy_endpoint: str):
    run_locust_test("all_cache_hits.py", proxy_endpoint)

def run_no_cache_hits_locust_test(proxy_endpoint: str):
    run_locust_test("no_cache_hits.py", proxy_endpoint)

def run_cache_off_locust_test(proxy_endpoint: str):
    run_locust_test("no_cache.py", proxy_endpoint)

def run_large_user_locust_test(script_name, proxy_endpoint: str):
    try:
        command = [
            "locust",
            "-f", script_name,
            "--headless",
            "-u", "100",
            "-r", "100",
            "-H", f"{proxy_endpoint}/",
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

def run_large_all_cache_hits_locust_test(proxy_endpoint: str):
    run_large_user_locust_test("all_cache_hits.py", proxy_endpoint)

def run_large_no_cache_hits_locust_test(proxy_endpoint: str):
    run_large_user_locust_test("no_cache_hits.py", proxy_endpoint)

def run_large_cache_off_locust_test(proxy_endpoint: str):
    run_large_user_locust_test("no_cache.py", proxy_endpoint)

def run_large_no_cache_hits_azure_locust_test(proxy_endpoint: str):
    run_large_user_locust_test("no_cache_hits_azure.py", proxy_endpoint)


