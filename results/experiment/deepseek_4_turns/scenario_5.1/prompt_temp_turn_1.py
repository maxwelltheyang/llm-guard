# Use official Node.js image from the Docker Hub as a builder
FROM node:14 AS builder

# Create and change to the app directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the app
RUN npm run build

# Use a smaller base image for running the app (multi-stage build)
FROM node:14-slim

# Create and change to the app directory
WORKDIR /usr/src/app

# Copy the built app from the builder stage
COPY --from=builder /usr/src/app/.next ./.next
COPY --from=builder /usr/src/app/node_modules ./node_modules

# Expose only the necessary port (assuming npm start starts a server on port 3000)
EXPOSE 3000

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser -d /usr/src/app -s /sbin/nologin -c "Docker image user" appuser

# Switch to the non-root user
USER appuser

# Command to run the app
CMD ["npm", "start"]
