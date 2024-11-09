# Use an official Python runtime as a base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the necessary dependencies
RUN pip install flask requests pygal

# Expose port 5000 for the Flask app
EXPOSE 5000

# Define environment variable for Flask
ENV FLASK_APP=app.py

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
