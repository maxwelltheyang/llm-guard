# Stage 1: Build the application
FROM node:18 as build

# Set the working directory within the container
WORKDIR /usr/src/app

# Copy the package.json and package-lock.json to the container
COPY package*.json ./

# Install the application dependencies inside the container
RUN npm install --only=production

# Copy the rest of the application code to the container
COPY . .

# Build the application
RUN npm run build

# Stage 2: Run the application
FROM node:18-slim

# Set the working directory within the container
WORKDIR /usr/src/app

# Copy the node_modules and built app from the build stage
COPY --from=build /usr/src/app/node_modules ./node_modules
COPY --from=build /usr/src/app/dist ./dist

# Copy only the necessary files for production
COPY --from=build /usr/src/app/package*.json ./

# Switch to a non-root user
RUN useradd --no-log-init -r -s /bin/false appuser
USER appuser

# Expose only the necessary non-root port the app runs on
EXPOSE 8080

# Use the npm 'ci' command for optimized and secure installation in production
CMD ["npm", "start"]
