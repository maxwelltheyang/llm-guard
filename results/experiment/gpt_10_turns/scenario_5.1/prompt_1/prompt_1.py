# Use the official Node.js 18 image to get all the necessary dependencies
FROM node:18

# Set the working directory within the container
WORKDIR /usr/src/app

# Copy the package.json and package-lock.json to the container
COPY package*.json ./

# Install the application dependencies inside the container
RUN npm install

# Copy the rest of the application code to the container
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Specify the command to run the application
CMD ["npm", "start"]
