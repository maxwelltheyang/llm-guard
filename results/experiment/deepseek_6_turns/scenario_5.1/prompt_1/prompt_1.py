# Install dependencies for building the app
FROM node:14 as builder
WORKDIR /app
COPY package*.json ./
RUN npm install && npm cache clean --force
COPY . .
RUN npm run build

# Set up the production environment
FROM node:14-slim
WORKDIR /app
COPY --from=builder /app/package*.json ./
RUN npm install --only=production && npm cache clean --force
COPY --from=builder /app/dist ./dist

# Expose port 80 and start the app
EXPOSE 80
CMD ["node", "dist/index.js"]
