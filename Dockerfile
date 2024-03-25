# Use a base image with necessary dependencies (e.g., Python)
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Update pip
RUN pip install --upgrade pip

# Install project dependencies
RUN pip install -r requirements.txt

# Copy other necessary files into the container
COPY deploy_and_run.sh .
COPY Locustfile.py .
COPY interpret_load_test.py .

# Make the bash script executable
RUN chmod +x deploy_and_run.sh

# Run the bash script when the container starts
CMD ["./deploy_and_run.sh"]
