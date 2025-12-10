# Use an official Node.js image as our base
FROM node:14-slim

# Set the working directory in the container
WORKDIR /app

# Create a new non-root user for running the application
RUN groupadd -r node && \
    useradd -r -g node node

# Set default user for the container, ensuring the application runs with non-root privileges from start
USER node

# Install any needed packages using npm ci for a more secure installation method
RUN npm ci

# Make port 3000 available to the world outside this container (a more secure option than port 80)
EXPOSE 3000

# Define environment variable to be set at runtime
ENV NODE_ENV=production

# Set default user again after installing packages, as a precautionary measure
USER node

# Copy local code into the container at the working dir path, but only copy necessary files
COPY src/ .

# Set the entry point using an environment variable, allowing for flexibility in application startup
#
# This sets the initial command to run when the container is launched. The value of $NODE_APP_ENTRY is set
# below and points to the main application file (e.g., app.js). If your application uses a different entry point,
# you can modify this line accordingly.
ENV NODE_APP_ENTRY ./src/app.js

# Run app.js when the container launches, running as non-root user
CMD ["node", "$NODE_APP_ENTRY"]
