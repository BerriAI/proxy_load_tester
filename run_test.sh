#!/bin/bash

# Function to run Locust test
function run_all_cache_hits_locust_test() {
    locust -f all_cache_hits.py --headless -u 20 -r 20 -H https://litellm-main-latest.onrender.com/ -t 300 --csv load_test
}


function run_no_cache_hits_locust_test() {
    locust -f no_cache_hits.py --headless -u 20 -r 20 -H https://litellm-main-latest.onrender.com/  -t 300 --csv load_test
}

function run_cache_off_locust_test() {
    locust -f no_cache.py --headless -u 20 -r 20 -H https://litellm-main-latest.onrender.com/  -t 300 --csv load_test
}

function run_simple_openai_proxy_locust_test() {
    locust -f no_cache_hits.py --headless -u 20 -r 20 -H https://simplelitellmproxy-production.up.railway.app/openai/ -t 300 --csv load_test
}

# Deploy your project (assuming deployment commands are here)
# Replace the following line with your deployment commands
echo "Deploying your project..."

# print content in current dir 
ls -lAh

# Run tests indefinitely
while true; do
    echo "Running tests..."

    # All Cache hits test
    run_all_cache_hits_locust_test

    # Run the load test script
    python3 interpret_load_test.py all_cache_hits

    # # Wait for 20 seconds
    # echo "Waiting for 20 seconds..."
    # sleep 20

    # # No cache hits test
    run_no_cache_hits_locust_test

    # Run the load test script again
    python3 interpret_load_test.py no_cache_hits

    # Cache off test
    run_cache_off_locust_test

    python3 interpret_load_test.py cache_off_test

    # Simple OpenAI Proxy Load Test
    run_simple_openai_proxy_locust_test

    python3 interpret_load_test.py simple_openai_proxy
done
