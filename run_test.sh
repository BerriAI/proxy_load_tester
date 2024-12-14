#!/bin/bash

# Function to run Locust test

function run_failed_responses_chat_completion() {
    locust -f failed_responses.py --headless -u 20 -r 20 -H https://https://litellm-production-6ee2.up.railway.app// -t 300 --csv load_test
}

function run_all_cache_hits_locust_test() {
    locust -f all_cache_hits.py --headless -u 20 -r 20 -H https://https://litellm-production-6ee2.up.railway.app// -t 300 --csv load_test
}


function run_no_cache_hits_locust_test() {
    locust -f no_cache_hits.py --headless -u 20 -r 20 -H https://https://litellm-production-6ee2.up.railway.app// -t 300 --csv load_test
}

function run_cache_off_locust_test() {
    locust -f no_cache.py --headless -u 20 -r 20 -H https://https://litellm-production-6ee2.up.railway.app// -t 300 --csv load_test
}


    python3 should_run_test.py # polls github to check if new release, once there is breaks out of loop

    # # Wait for 20 seconds
    # echo "Waiting for 20 seconds..."
    # sleep 20

    # No cache hits test
    run_no_cache_hits_locust_test

    # Run the load test script again
    python3 interpret_load_test.py no_cache_hits

    # Cache off test
    run_cache_off_locust_test

    python3 interpret_load_test.py cache_off_test

        # All Cache hits test
    run_all_cache_hits_locust_test

    # Run the load test script
    python3 interpret_load_test.py all_cache_hits


done
