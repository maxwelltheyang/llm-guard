# Stage 1: Build the application
FROM node:16 AS build

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json files to the working directory
COPY package*.json ./

# Install the Node.js dependencies
RUN npm ci --only=production

# Copy the rest of the application code to the working directory
COPY . .

# Build the application (assumes a build script is defined in package.json)
RUN npm run build

# Stage 2: Use a smaller base image for running the application
FROM node:16-slim AS production

# Set the working directory inside the container
WORKDIR /app

# Copy the compiled application from the build stage
COPY --from=build /app .

# Install only production dependencies
RUN npm ci --only=production && npm cache clean --force

# Create a non-root user and switch to it
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Change the default port of the application, assuming it's configurable
# Use a non-privileged port (above 1024)
ENV PORT 8080
EXPOSE 8080

USER appuser

# Define the command to run the application
CMD ["npm", "start"]
