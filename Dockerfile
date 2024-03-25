# Use a base image with necessary dependencies (e.g., Python, Locust, etc.)
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .


# Install any additional dependencies required for your project
RUN pip install -r requirements.txt

# Make the bash script executable
RUN chmod +x deploy_and_run.sh

# Run the bash script when the container starts
CMD ["./deploy_and_run.sh"]
