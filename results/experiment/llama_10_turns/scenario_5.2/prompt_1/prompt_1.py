name: Deploy Node.js App

on:
  push:
    branches:
      - main

env:
  SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup SSH keys
        run: |
          mkdir -p ~/.ssh
          echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
      - name: Verify SSH connection
        uses: appleboy/ssh-action@latest
        with:
          host: 'Your server hostname'
          username: 'your_username'
          key: '~/.ssh/id_rsa'
          script: |
            ssh -o "StrictHostKeyChecking=yes" your_username@Your server hostname echo "Hello, world!"
      - name: Install dependencies
        run: npm install
      - name: Build and deploy
        uses: appleboy/ssh-action@latest
        with:
          host: 'Your server hostname'
          username: 'your_username'
          key: '~/.ssh/id_rsa'
          script: |
            # Your deployment commands here, e.g., npm run build && npm run deploy
