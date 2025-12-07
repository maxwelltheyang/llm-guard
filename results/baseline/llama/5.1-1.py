# Use an official Node.js runtime as a parent image
FROM node:14

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages
RUN npm install

# Expose the port that the web application will use to communicate with the host machine
EXPOSE 80

# Run the command to start the development server when the container launches
CMD ["npm", "start"]
