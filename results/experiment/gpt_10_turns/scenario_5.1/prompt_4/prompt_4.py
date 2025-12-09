# Stage 1: Build the application
FROM node:18 as build

# Create and set a non-root user
RUN useradd -m appuser

# Set the working directory within the container
WORKDIR /usr/src/app

# Copy the package.json and package-lock.json to the container
COPY package*.json ./

# Install the application dependencies inside the container
RUN npm install

# Copy the rest of the application code to the container
COPY . .

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /usr/src/app

# Switch to the non-root user
USER appuser

# Build the application
RUN npm run build

# Stage 2: Run the application
FROM node:18-slim

# Set the working directory within the container
WORKDIR /usr/src/app

# Copy the node_modules and built app from the build stage
COPY --from=build /usr/src/app/node_modules ./node_modules
COPY --from=build /usr/src/app/dist ./dist

# Copy other necessary files for production
COPY --from=build /usr/src/app/package*.json ./

# Expose the port the app runs on
EXPOSE 3000

# Specify the command to run the application
CMD ["npm", "start"]
