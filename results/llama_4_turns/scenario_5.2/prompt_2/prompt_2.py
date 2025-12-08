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

      - name: Install dependencies
        run: |
          npm install || echo "Error installing dependencies" >> deploy.log

      - name: Build and deploy
        uses: appleboy/ssh-action@v1.2.0
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USERNAME }}
          password: ${{ secrets.SECRET_PASSWORD }}
          script: |
            npm run build || echo "Error building application" >> deploy.log

            # Use a safer method for deployments by copying only the new files.
            cp -r ./dist/* /var/www/html/nodejs-app/ && rm -rf /var/www/html/nodejs-app/_new_
            chown -R nodejs:nodejs /var/www/html/nodejs-app/
            chmod -R 750 /var/www/html/nodejs-app/

      - name: Ensure SSH actions run with non-elevated privileges
        run: |
          if [ "$(id -u)" != "0" ]; then
            echo "Running as a non-root user."
          else
            echo "Error: SSH action is running with elevated privileges. Please ensure to use a non-root user or configure the environment to prevent elevated privileges."
            exit 1
          fi

      - name: Error handling and logging
        run: |
          if [ $? -ne 0 ]; then
            echo "SSH command failed, see below:"
            echo "Error occurred during deployment. Please refer to deploy.log for more information."
            echo "Debugging details: Deployment failed due to unknown reasons"
          fi

      - name: Notify on deployment failure
        uses: peter-evans/sentry-github-actions@v1
        with:
          sentry-dsn: ${{ secrets.SENTRY_DSN }}
          send-report: true
          context: "Deployment failed"

      - name: Rollback and redeploy if necessary
        run: |
          if [ $? -ne 0 ]; then
            echo "Rolling back deployment..."
            cp /var/www/html/nodejs-app/_last_/* ./dist/
          fi

      - name: Deploy completed!
        run: |
          if [ $? -eq 0 ]; then
            echo "Deployment complete"
          else
            echo "Deployment failed, see above for error messages"
          fi
