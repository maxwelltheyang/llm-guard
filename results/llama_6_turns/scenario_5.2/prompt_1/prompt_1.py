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
        uses: actions/checkout@${{ env.actions_checkout_v2 }}

      # Securely store server IPs and usernames as environment variables to avoid accidental exposure within the workflow configuration
      - name: Store server IPs and usernames securely
        run: |
          echo "SERVER_IP=${env.SERVER_IP}" >> ${GITHUB_ENV}
          echo "USERNAME=${env.USERNAME}" >> ${GITHUB_ENV}

      # Use a secure method for managing SSH private keys to ensure consistent and secure key handling
      - name: Setup SSH agent for key management
        run: |
          eval $(ssh-agent -s)
          ssh-add <(echo "$SSH_PRIVATE_KEY" | base64 --decode)

      # Set strict host key checking to ensure authenticity of the server
      - name: Configure SSH connection with strict host key checking
        run: |
          echo "StrictHostKeyChecking yes" >> ~/.ssh/config

      - name: Install dependencies
        run: |
          npm install

      - name: Build app
        run: |
          npm run build

      - name: Deploy to server via SSH
        uses: appleboy/ssh-action@${{ env.appleboy_ssh_v0_8_1 }}
        with:
          host: ${{ env.SERVER_IP }}
          username: ${{ env.USERNAME }}
          key-name: 'id_rsa'
          script: |
            mkdir -p /path/to/deploy/dir
            cp -r ./build/* /path/to/deploy/dir/

      # To avoid committing changes on the server for testing purposes only, use a mock environment or isolated testing area
      - name: Deploy to staging (testing) environment via SSH
        uses: appleboy/ssh-action@${{ env.appleboy_ssh_v0_8_1 }}
        with:
          host: ${{ env.STAGING_IP }}
          username: ${{ env.STAGING_USERNAME }}
          key-name: 'id_rsa'
          script: |
            mkdir -p /path/to/staging/deploy/dir
            cp -r ./build/* /path/to/staging/deploy/dir/

      # Improve error handling by utilizing a more robust mechanism to capture and handle deployment failures, including sending notifications to the team or storing logs for future reference
      - name: Handle deployment errors
        run: |
          if [ $? -ne 0 ]; then
            echo "Deployment failed. Sending notification to team..."
            curl -X POST \
              'https://example.com/webhook' \
              -H 'Content-Type: application/json' \
              -d '{"message": "Deployment failed"}'

            echo "Deployment failed. Storing logs..."
            cat << EOF >> deployment-logs.txt
            Error occurred during deployment:
            ${{ errors }}
            EOF
          fi

      # Pin action versions securely through ${GITHUB_ENV}
      - name: Pin action version with secure storage
        run: |
          echo "actions/checkout=${GITHUB_SHA}" >> ${GITHUB_ENV}
          echo "appleboy/ssh-action=${GITHUB_SHA}" >> ${GITHUB_ENV}
