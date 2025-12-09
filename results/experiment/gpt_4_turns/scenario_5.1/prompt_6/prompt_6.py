# Stage 1: Build the app
FROM node:18 AS builder

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install the application dependencies, ensuring no optional dependencies are installed
RUN npm ci --only=production

# Copy the rest of the application code to the working directory
COPY . .

# Build the application (if applicable)
RUN npm run build

# Stage 2: Run the app using a smaller base image
FROM node:18-slim

# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy only necessary files from the builder stage
COPY --from=builder /usr/src/app/package*.json ./
COPY --from=builder /usr/src/app/dist ./dist

# Install production dependencies only
RUN npm ci --only=production

# Change ownership of the app directory
RUN chown -R appuser:appgroup /usr/src/app

# Switch to the non-root user
USER appuser

# Use a non-root port like 8080
ENV PORT=8080

# Specify the port the app runs on
EXPOSE 8080

# Define the command to run the application
CMD ["npm", "start"]
