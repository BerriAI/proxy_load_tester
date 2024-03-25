#!/bin/bash

# Function to run Locust test
function run_locust_test() {
    locust -f locustfile.py --headless -u 100 -r 100 -H http://a472dc7c273fd47fd9a20434f463afd1-393291597.us-west-2.elb.amazonaws.com:4000/ -t 300 --csv load_test
}


# Function to run load test script
function run_load_test_script() {
    python3 interpret_load_test.py
}

# Deploy your project (assuming deployment commands are here)
# Replace the following line with your deployment commands
echo "Deploying your project..."

# print content in current dir 
ls -lAh

# Run tests indefinitely
while true; do
    echo "Running tests..."

    # Run the initial Locust test
    run_locust_test

    # Run the load test script
    run_load_test_script

    # Wait for 20 seconds
    echo "Waiting for 20 seconds..."
    sleep 20

    # Run the Locust test loop again
    run_locust_test

    # Run the load test script again
    run_load_test_script
done
