# Install dependencies for building the app
FROM node:14 as builder
WORKDIR /app
COPY package*.json ./
RUN npm install && npm cache clean --force
COPY . .
RUN npm run build

# Use a smaller base image for running the app
FROM node:14-slim
WORKDIR /app
COPY --from=builder /app/package*.json ./
RUN npm install --only=production && npm cache clean --force
COPY --from=builder /app/dist ./dist

# Set environment variables if needed
ENV ENV_VARIABLE=value

# Expose port 80 and start the app
EXPOSE 80
USER node
CMD ["node", "dist/index.js"]
