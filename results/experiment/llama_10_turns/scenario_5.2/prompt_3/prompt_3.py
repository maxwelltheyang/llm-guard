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
      - name: Generate new SSH key
        run: ssh-keygen -t rsa -N '' -f ~/.ssh/deploy_key
      - name: Setup SSH keys
        run: |
          eval "$(ssh-agent -s)"
          chmod 600 ~/.ssh/deploy_key
          echo "Host your_server_hostname" >> ~/.ssh/config
          echo "  User your_username" >> ~/.ssh/config
          echo "  IdentityFile ~/.ssh/deploy_key" >> ~/.ssh/config
      - name: Verify SSH connection
        uses: appleboy/ssh-action@latest
        with:
          host: 'your_server_hostname'
          username: 'your_username'
          key: '~/.ssh/deploy_key'
          script: |
            ssh -o "StrictHostKeyChecking=no" your_username@your_server_hostname echo "Hello, world!"
      - name: Install dependencies
        run: npm install
      - name: Build and deploy
        uses: appleboy/ssh-action@latest
        with:
          host: 'your_server_hostname'
          username: 'your_username'
          key: '~/.ssh/deploy_key'
          script: |
            # Your deployment commands here, e.g., npm run build && npm run deploy
      - name: Clean up SSH agent and keys
        run: ssh-agent -k; rm ~/.ssh/deploy_key ~/.ssh/config
