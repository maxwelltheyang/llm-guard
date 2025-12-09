# Use the latest stable version of Node.js and slim variant as builder stage
FROM node:20-slim AS builder

# Pin Node.js version for reproducibility
RUN npx --no-install npm@6.14.0 install --only=production --legacy-peer-deps && \
    npm install -g npm@6.14.0

# Change to the app directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install only production dependencies with a specific version (e.g., npm@6.14.0)
RUN npm install --only=production@6.14.0 --legacy-peer-deps && npm install -g npm@6.14.0

# Copy the rest of the application code
COPY . .

# Build the app
RUN npm run build

# Use a smaller base image for running the app (multi-stage build)
FROM alpine:latest

# Create a non-root user and switch to it immediately for security best practices
RUN adduser -D myuser

# Change to the app directory
WORKDIR /usr/src/app

# Copy the built app from the builder stage
COPY --from=builder /usr/src/app/dist ./dist

# Expose port 3000 to the outside world
EXPOSE 3000

# Command to run the app as the non-root user
USER myuser

# Install only production dependencies with a specific version (e.g., npm@6.14.0)
RUN npm install --only=production@6.14.0 --legacy-peer-deps && npm install -g npm@6.14.0

# Cleanup and minimize layers by combining commands
RUN rm -rf /usr/src/app/{node_modules,*.npm} && chown -R myuser:myuser /usr/src/app

# Use a more descriptive environment variable name if needed
ENV APP_ENVIRONMENT production
