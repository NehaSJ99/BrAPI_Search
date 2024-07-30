# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Assuming your server_info.json is in the root directory of your project
COPY server_info.json /server_info.json

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose port 5000 for the application (adjust if needed)
EXPOSE 5000

# Command to run the application
CMD ["python", "run.py"]
