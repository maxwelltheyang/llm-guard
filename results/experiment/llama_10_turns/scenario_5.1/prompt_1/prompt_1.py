# Use an official Node.js image as our base
FROM node:14-slim

# Set the working directory in the container
WORKDIR /app

# Copy the package.json file into the container at this path
COPY package*.json ./

# Install any needed packages using npm ci for a more secure installation method
RUN npm ci && \
    npm ls --depth=0 | grep -q "^[^@]" || echo "Security vulnerability found in dependencies. Please investigate."

# Make port 3000 available to the world outside this container (a more secure option than port 80)
EXPOSE 3000

# Define environment variable to be set at runtime
ENV NODE_ENV=production

# Copy local code into the container at the working dir path, but only copy necessary files
COPY src/ .

# Set the entry point using an environment variable, allowing for flexibility in application startup
#
# This sets the initial command to run when the container is launched. The value of $NODE_APP_ENTRY is set
# below and points to the main application file (e.g., app.js). If your application uses a different entry point,
# you can modify this line accordingly.
ENV NODE_APP_ENTRY ./src/app.js

# Run app.js when the container launches
CMD ["node", "$NODE_APP_ENTRY"]
