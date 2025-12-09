# Use official Node.js image from the Docker Hub
FROM node:14

# Create and change to the app directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port 3000 to the outside world
EXPOSE 3000

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser -d /usr/src/app -s /sbin/nologin -c "Docker image user" appuser

# Switch to the non-root user
USER appuser

# Command to run the app
CMD ["npm", "start"]
