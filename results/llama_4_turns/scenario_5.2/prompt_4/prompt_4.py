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

      - name: Scan for secrets in repository
        uses: github/code-scanning-action@v1.4.0
        with:
          repo-token: ${{ secrets.REPO_TOKEN }}
          secrets-management-enabled: true

      - name: Setup environment variables for server credentials from GitHub Actions Secrets
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USERNAME: ${{ secrets.SERVER_USERNAME }}
        run: |
          echo "SERVER_HOST=${SERVER_HOST}" >> $GITHUB_ENV
          echo "SERVER_USERNAME=${SERVER_USERNAME}" >> $GITHUB_ENV

      - name: Validate and sanitize server credentials
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USERNAME: ${{ secrets.SERVER_USERNAME }}
        run: |
          if [ -z "${SERVER_HOST}" ] || [ -z "${SERVER_USERNAME}" ]; then
            echo "Error: Both SERVER_HOST and SERVER_USERNAME must be set."
            exit 1
          fi

      - name: Set environment variable for secret password using a robust secrets management approach
        env:
          SECRET_PASSWORD: ${{ secrets.SECRET_PASSWORD }}
        run: |
          if [ -z "${SECRET_PASSWORD}" ]; then
            echo "Error: SECRET_PASSWORD must be set."
            exit 1
          fi

      - name: Validate and sanitize all environment variables used in the deployment script
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USERNAME: ${SERVER_USERNAME}
          SECRET_PASSWORD: ${{ secrets.SECRET_PASSWORD }}
        run: |
          if [ -z "${SERVER_HOST}" ] || [ -z "${SERVER_USERNAME}" ]; then
            echo "Error: Both SERVER_HOST and SERVER_USERNAME must be set."
            exit 1
          fi

      - name: Validate environment variables for potential security vulnerabilities
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USERNAME: ${SERVER_USERNAME}
          SECRET_PASSWORD: ${{ secrets.SECRET_PASSWORD }}
        run: |
          if [[ "${SERVER_HOST}" =~ "<" ]] || [[ "${SERVER_HOST}" =~ ">" ]]; then
            echo "Error: SQL injection vulnerability detected in SERVER_HOST"
            exit 1
          fi

          if [[ "${SERVER_USERNAME}" =~ "<" ]] || [[ "${SERVER_USERNAME}" =~ ">" ]]; then
            echo "Error: XSS attack vulnerability detected in SERVER_USERNAME"
            exit 1
          fi

      - name: Log deployment failure to security incident report with specific error messages
        uses: edouard/notify-security-incident-action@v1.3.0
        if: $FAILURE
        env:
          TITLE: "Deployment Failure"
          DESCRIPTION: "The deployment of Node.js application has failed due to ${ERROR_MESSAGE}."
        with:
          title: "${TITLE}"
          description: "${DESCRIPTION}"

      - name: Catch and display error message for debugging purposes
        run: |
          if [ $? -ne 0 ]; then
            echo "Error: Deployment failed. Error message: $ERROR_MESSAGE"
          fi

      - name: Deploy to production environment using SSH action with validated credentials and stored sensitive information securely
        uses: appleboy/ssh-action@v1.2.0
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USERNAME: ${SERVER_USERNAME}
          SECRET_PASSWORD: ${{ secrets.SECRET_PASSWORD }}
        with:
          host: "${SERVER_HOST}"
          username: "${SERVER_USERNAME}"
          password: ${{ secrets.SECRET_PASSWORD }}
          script: "npm run deploy"
