# Use an official Node.js image as our base for building the app
FROM node:14-bullseye-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Create a new non-root user for running the application and install packages
RUN groupadd -r node && \
    useradd -r -g node node && \
    USER=node npm ci

# Make port 3000 available to the world outside this container (a more secure option than port 80)
ENV EXPOSED_PORT=3000
EXPOSE $EXPOSED_PORT

# Define environment variables for build and runtime
ENV NODE_ENV=production
ENV APP_DIR=/usr/src/app

# Set entry point and build app
ENV NODE_APP_ENTRY ./src/app.js
RUN npm run build

# Use a smaller base image for running the app
FROM node:14-alpine

# Copy the built app into this new stage
COPY --from=builder /app/src .

# Run the app from the specified working directory
WORKDIR $APP_DIR

# This command is removed as it's not suitable for production environments
# CMD ["node", "$NODE_APP_ENTRY"]
