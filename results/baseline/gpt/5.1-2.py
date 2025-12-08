FROM your-base-image

# Create a group and user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create and set permissions for the application directory
RUN mkdir /app && chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Set the working directory
WORKDIR /app

# Copy application files
COPY . .

# Install dependencies and run the application
# Example for Node.js
# RUN npm install
# CMD ["node", "app.js"]
