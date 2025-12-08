# Check if the Dockerfile starts with a FROM instruction
FROM python:3.9-slim AS base

# The base image is set to Python 3.9-slim, which is a minimal version of the Python base image
WORKDIR /app

# Copy the requirements file from the current directory into the working directory
COPY requirements.txt .

# Install the dependencies specified in the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code from the current directory into the working directory
COPY . .

# The RUN instruction is used to execute a command, but it's not clear what this command is doing.
# It would be better to use a separate script for installing dependencies and running the application.
RUN ["pip", "install", "-r", "/app/requirements.txt"]

# Expose port 80 so that the container can be accessed from outside
EXPOSE 80

# The final image will inherit all the layers created above, including the base image.
# This is done to ensure that any changes made to the Dockerfile are applied correctly.
FROM base AS final

# Copy the application code into the final image
COPY --from=0 /app .

# Run the command to start the web server when the container starts
CMD ["gunicorn", "main:app"]
