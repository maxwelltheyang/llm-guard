# Use the official Node.js 18 image to get all the necessary dependencies
FROM node:18

# Create and set a non-root user
RUN useradd -m appuser

# Set the working directory within the container
WORKDIR /usr/src/app

# Copy the package.json and package-lock.json to the container
COPY package*.json ./

# Install the application dependencies inside the container
RUN npm install

# Copy the rest of the application code to the container
COPY . .

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /usr/src/app

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 3000

# Specify the command to run the application
CMD ["npm", "start"]
