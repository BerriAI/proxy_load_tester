#!/bin/bash

# Function to run Locust test
function run_all_cache_hits_locust_test() {
    locust -f all_cache_hits.py --headless -u 100 -r 100 -H http://a472dc7c273fd47fd9a20434f463afd1-393291597.us-west-2.elb.amazonaws.com:4000/ -t 300 --csv load_test
}


function run_no_cache_hits_locust_test() {
    locust -f no_cache_hits.py --headless -u 100 -r 100 -H http://a472dc7c273fd47fd9a20434f463afd1-393291597.us-west-2.elb.amazonaws.com:4000/ -t 300 --csv load_test
}

function run_cache_off_locust_test() {
    locust -f no_cache.py --headless -u 100 -r 100 -H http://a472dc7c273fd47fd9a20434f463afd1-393291597.us-west-2.elb.amazonaws.com:4000/ -t 300 --csv load_test
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

    # Wait for 20 seconds
    echo "Waiting for 20 seconds..."
    sleep 20

    # No cache hits test
    run_no_cache_hits_locust_test

    # Run the load test script again
    python3 interpret_load_test.py no_cache_hits

    # Cache off test
    run_cache_off_locust_test

    python3 interpret_load_test.py cache_off_test
done
