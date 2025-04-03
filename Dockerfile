# Use a slim version of the official Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy dependency definitions file (if you have one)
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the working directory
COPY . .

# Command to run the bot
CMD ["python3", "main.py"]
