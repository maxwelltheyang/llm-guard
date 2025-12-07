# Stage 1: Build the application
FROM node:14 AS build

WORKDIR /app

COPY package.json .

RUN npm install

COPY . .

RUN npm run build

# Stage 2: Create a smaller image for running the application
FROM node:14-slim

WORKDIR /app

COPY --from=build /app/build ./build
COPY --from=build /app/node_modules ./node_modules
COPY package.json .

CMD ["node", "build/server.js"]
