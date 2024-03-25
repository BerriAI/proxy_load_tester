# Use a base image with necessary dependencies (e.g., Python, Locust, etc.)
FROM python:3.9-slim

# Install any additional dependencies required for your project
RUN pip install -r requirements.txt


# Set the working directory in the container
WORKDIR /app

# Copy the required files into the container
COPY deploy_and_run.sh .
COPY Locustfile.py .
COPY interpret_load_test.py .

# Make the bash script executable
RUN chmod +x deploy_and_run.sh

# Run the bash script when the container starts
CMD ["./deploy_and_run.sh"]
