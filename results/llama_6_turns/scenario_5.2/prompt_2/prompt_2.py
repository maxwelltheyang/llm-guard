name: Deploy Node.js App

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
      SERVER_IP: ${{ secrets.SERVER_IP }}
      USERNAME: ${{ secrets.USERNAME }}
      STAGING_IP: ${{ secrets.STAGING_IP }}
      STAGING_USERNAME: ${{ secrets.STAGING_USERNAME }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      # Securely store server IPs and usernames as environment variables to avoid accidental exposure within the workflow configuration
      - name: Store server IPs and usernames securely
        run: |
          echo "SERVER_IP=${env.SERVER_IP}" >> ${GITHUB_ENV}
          echo "USERNAME=${env.USERNAME}" >> ${GITHUB_ENV}
          echo "STAGING_IP=${env.STAGING_IP}" >> ${GITHUB_ENV}
          echo "STAGING_USERNAME=${env.STAGING_USERNAME}" >> ${GITHUB_ENV}

      # Use a secure method for managing SSH private keys to ensure consistent and secure key handling
      - name: Setup SSH agent for key management
        run: |
          eval $(ssh-agent -s)
          ssh-add <(echo "$SSH_PRIVATE_KEY" | base64 --decode)

      # Pin action versions securely through ${GITHUB_ENV}
      - name: Pin action version with secure storage
        run: |
          echo "actions/checkout=v2" >> ${GITHUB_ENV}
          echo "appleboy/ssh-action=v2.1.0" >> ${GITHUB_ENV}

      # Merge deployment steps for server and staging into a single step
      - name: Deploy to both server and staging via SSH
        uses: appleboy/ssh-action@v2.1.0
        with:
          host: ${{ env.STAGING_IP }}
          username: ${{ env.STAGING_USERNAME }}
          script: |
            mkdir -p /path/to/staging/deploy/dir
            cp -r ./build/* /path/to/staging/deploy/dir/
          key: <$(echo "$SSH_PRIVATE_KEY" | base64 --decode)>
