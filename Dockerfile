# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first, if you have one (for dependency caching)
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
# This assumes you have a requirements.txt file in your project
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Expose port 80 (or whatever port your app runs on)
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]