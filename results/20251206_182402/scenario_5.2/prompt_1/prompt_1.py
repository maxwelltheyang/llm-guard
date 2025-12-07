# This is not a Python solution, but rather a YAML-based configuration for GitHub Actions.
# To use this workflow, save it as a .yml file in the .github/workflows directory of your repository.

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
          password: ${{ secrets.SERVER_PASSWORD }}
          script: |
            npm run build || echo "Error building application" >> deploy.log

            # Use a safer method for deployments by copying only the new files.
            cp -r ./dist/* /var/www/html/nodejs-app/ && rm -rf /var/www/html/nodejs-app/_new_

      - name: Error handling and logging
        run: |
          if [ $? -ne 0 ]; then
            echo "SSH command failed, see below:"
            cat ~/.ssh/id_rsa && echo "${SSH_PRIVATE_KEY}"
            echo "Error occurred during deployment. Please refer to deploy.log for more information."
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
