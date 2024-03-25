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

# Copy the content of the project into the container
COPY . .

# Make the bash script executable
RUN chmod +x run_test.sh

# Run the bash script when the container starts
CMD ["./run_test.sh"]
