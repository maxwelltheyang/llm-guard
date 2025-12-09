# Use the latest stable version of Node.js and slim variant
FROM node:20-slim

# Create a non-root user and switch to it immediately for security best practices
# This ensures that any potential vulnerabilities in the application do not affect the root user or system
RUN useradd -m myuser && su - myuser

# Change to the app directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install && npm cache clean --force

# Copy the rest of the application code
COPY . .

# Expose port 3000 to the outside world
EXPOSE 3000

# Command to run the app as the non-root user
CMD ["npm", "start"]
