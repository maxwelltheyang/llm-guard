# Use the official Node.js 16 LTS image as the base image
FROM node:16

# Create and set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json files to the working directory
COPY package*.json ./

# Install the Node.js dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Create a non-root user and switch to it
RUN useradd --user-group --create-home --shell /bin/false appuser
USER appuser

# Expose the port the app runs on
EXPOSE 3000

# Define the command to run the application
CMD ["npm", "start"]
