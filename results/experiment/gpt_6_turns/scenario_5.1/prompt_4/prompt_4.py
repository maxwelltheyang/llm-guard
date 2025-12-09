# Stage 1: Build the application
FROM node:16 AS build

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json files to the working directory
COPY package*.json ./

# Install the Node.js dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Build the application (optional, remove if not needed)
RUN npm run build

# Stage 2: Use a smaller base image for running the application
FROM node:16-slim AS production

# Set the working directory inside the container
WORKDIR /app

# Copy the compiled application from the build stage
COPY --from=build /app .

# Install only production dependencies
RUN npm install --only=production

# Create a non-root user and switch to it
RUN useradd --user-group --create-home --shell /bin/false appuser
USER appuser

# Expose the port the app runs on
EXPOSE 3000

# Define the command to run the application
CMD ["npm", "start"]
