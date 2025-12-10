# Use official Node 14 image as base
FROM node:14-alpine

# Create /app directory if it doesn't exist
RUN mkdir -p /app

# Set working directory to /app
WORKDIR /app

# Copy package.json to /app
COPY package.json /app/

# Install dependencies using npm ci in a separate RUN instruction
RUN npm ci

# Build the application (assumes npm run build is used for building)
RUN npm run build

# Copy remaining files
COPY . .

# Expose port 3000, this will be used as default port when running the container with docker run
EXPOSE 3000

# Define a health check to ensure the container is running correctly
HEALTHCHECK --timeout=5s --interval=10s CMD ["npm", "run", "healthcheck"]

CMD ["npm", "start"]
