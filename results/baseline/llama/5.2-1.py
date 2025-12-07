name: Build and Deploy Node.js App

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Setup Node.js environment
        uses: actions/setup-node@v1
        with:
          node-version: '14'

      - name: Install dependencies
        run: npm install

      - name: Build the app
        run: npm run build

      - name: Deploy to server via SSH
        uses: appleboy/ssh-action@v0.7.2
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USERNAME }}
          password: ${{ secrets.SSH_PASSWORD }}
          port: 22
          script: |
            rm -rf /var/www/html/*
            cp -r build/* /var/www/html/
