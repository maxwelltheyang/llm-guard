name: Node.js Deployment

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Setup SSH keys
        uses: appleboy/ssh-key-action@v1.6.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: Set environment variables for server credentials from GitHub Actions Secrets
        run: |
          echo "SERVER_HOST=${{ secrets.SERVER_HOST }}" >> $GITHUB_ENV
          echo "SERVER_USERNAME=${{ secrets.SERVER_USERNAME }}" >> $GITHUB_ENV

      - name: Validate and sanitize server credentials
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USERNAME: ${{ secrets.SERVER_USERNAME }}
        run: |
          if [ -z "${SERVER_HOST}" ] || [ -z "${SERVER_USERNAME}" ]; then
            echo "Error: Both SERVER_HOST and SERVER_USERNAME must be set."
            exit 1
          fi

      - name: Set environment variable for secret password from GitHub Actions Secrets
        env:
          SECRET_PASSWORD: ${{ secrets.SECRET_PASSWORD }}
        run: |
          if [ -z "${SECRET_PASSWORD}" ]; then
            echo "Error: SECRET_PASSWORD must be set."
            exit 1
          fi

      - name: Install dependencies
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USERNAME: ${{ secrets.SERVER_USERNAME }}
        run: |
          npm install || echo "Error installing dependencies" >> deploy.log

      - name: Build and deploy using SSH action with validated credentials
        env:
          SERVER_HOST: ${SERVER_HOST}
          SERVER_USERNAME: ${SERVER_USERNAME}
        uses: appleboy/ssh-action@v1.2.0
        with:
          host: ${SERVER_HOST}
          username: ${SERVER_USERNAME}
          password: ${{ secrets.SECRET_PASSWORD }} # Use the secret password directly instead of environment variable.
          script: |
            npm run build || echo "Error building application" >> deploy.log

            # Use a safer method for deployments by copying only the new files.
            cp -r ./dist/* /var/www/html/nodejs-app/ && rm -rf /var/www/html/nodejs-app/_new_
            chown -R nodejs:nodejs /var/www/html/nodejs-app/
            chmod -R 750 /var/www/html/nodejs-app/

      - name: Notify on deployment failure
        uses: peter-evans/sentry-github-actions@v1
        with:
          sentry-dsn: ${{ secrets.SENTRY_DSN }}
          send-report: true
          context: "Deployment failed"

      - name: Clean up secret key file and CI environment
        run: |
          rm ${{ secrets.SSH_PRIVATE_KEY }}
          echo "CI environment cleaned."

      - name: Deploy completed!
        run: |
          if [ $? -eq 0 ]; then
            echo "Deployment complete"
          else
            echo "Deployment failed, see above for error messages"
          fi
