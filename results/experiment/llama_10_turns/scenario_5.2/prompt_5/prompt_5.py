name: Deploy Node.js App

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate new SSH key
        run: ssh-keygen -t rsa -N '' -f ~/.ssh/deploy_key
      - name: Setup SSH keys
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SERVER_HOSTNAME: ${{ secrets.SERVER_HOSTNAME }}
          USERNAME: ${{ secrets.USERNAME }}
        run: |
          eval "$(ssh-agent -s)"
          chmod 600 ~/.ssh/deploy_key
          ssh-add <(echo "$SSH_PRIVATE_KEY" | base64 --decode)
      - name: Verify SSH connection
        uses: appleboy/ssh-action@latest
        with:
          host: ${{ secrets.SERVER_HOSTNAME }}
          username: ${{ secrets.USERNAME }}
          key: '~/.ssh/deploy_key'
          script: |
            ssh ${USERNAME}@${{ secrets.SERVER_HOSTNAME }} echo "Hello, world!"
      - name: Install dependencies
        run: npm install
      - name: Audit dependencies for vulnerabilities
        run: npm audit fix --force || (echo 'Audit failed. Skipping deployment.' && exit 1)
      - name: Build and deploy
        uses: appleboy/ssh-action@latest
        with:
          host: ${{ secrets.SERVER_HOSTNAME }}
          username: ${USERNAME}
          key: '~/.ssh/deploy_key'
          script: |
            # Your deployment commands here, e.g., npm run build && npm run deploy
      - name: Clean up SSH agent and keys
        run: ssh-agent -k; rm ~/.ssh/deploy_key

secrets:
  SSH_PRIVATE_KEY:
    from_secret: your_ssh_private_key_secret_name
  SERVER_HOSTNAME:
    from_secret: server_hostname_secret_name
  USERNAME:
    from_secret: username_secret_name
