# Use the official Node.js image from the Docker Hub
FROM node:18

# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install the application dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Change ownership of the app directory
RUN chown -R appuser:appgroup /usr/src/app

# Switch to the non-root user
USER appuser

# Specify the port the app runs on
EXPOSE 3000

# Define the command to run the application
CMD ["npm", "start"]
