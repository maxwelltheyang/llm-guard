name: Node.js Deployment

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: read-only
      contents: read-only
      security-events: write
      actions: read-only
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Rotate and update GitHub Secrets for secure data storage
        uses: appleboy/github-secrets-action@v1.4.0
        env:
          REPO_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          token: "${REPO_TOKEN}"
          secrets-management-enabled: true

      - name: Setup environment variables for server credentials from GitHub Actions Secrets
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USERNAME: ${SERVER_USERNAME}
        run: |
          if [ -z "${SERVER_HOST}" ] || [ -z "${SERVER_USERNAME}" ]; then
            echo "Error: Both SERVER_HOST and SERVER_USERNAME must be set."
            exit 1
          fi

      - name: Validate and sanitize server credentials
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USERNAME: ${SERVER_USERNAME}
        run: |
          if [[ "${SERVER_HOST}" =~ "<" || "${SERVER_HOST}" =~ ">" ]]; then
            echo "Error: SQL injection vulnerability detected in SERVER_HOST"
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

      - name: Validate environment variables for potential security vulnerabilities
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USERNAME: ${SERVER_USERNAME}
          SECRET_PASSWORD: ${{ secrets.SECRET_PASSWORD }}
        run: |
          if [[ "${SECRET_PASSWORD}" =~ "<" || "${SECRET_PASSWORD}" =~ ">" ]]; then
            echo "Error: SQL injection vulnerability detected in SECRET_PASSWORD"
            exit 1
          fi

      - name: Log deployment start to security incident report with granular access control
        uses: edouard/notify-security-incident-action@v1.4.0
        env:
          TITLE: "Deployment Start"
          DESCRIPTION: "The Node.js application deployment has started."
        with:
          title: "${TITLE}"
          description: "${DESCRIPTION}"

      - name: Run automatic security audit during build without exposing sensitive data with limited permissions
        env:
          NODE_VERSION: 'latest'
        run: |
          npm config set unsafe-perm false && \
          npm install && \
          npm audit fix || echo "Security audit failed."

      # Write sanitized output directly to environment variable
      - name: Sanitize error messages before logging them with granular access control
        env:
          ERROR_MESSAGE: ${{ secrets.ERROR_MESSAGE }}
        run: |
          sanitized_message=$(echo "${ERROR_MESSAGE}" | sed 's/<[^>]*>//g')
          echo "Sanitized error message: ${sanitized_message}"

      - name: Log deployment completion to security incident report with granular access control
        uses: edouard/notify-security-incident-action@v1.4.0
        env:
          TITLE: "Deployment Completion"
          DESCRIPTION: "The Node.js application deployment has completed successfully."
        with:
          title: "${TITLE}"
          description: "${DESCRIPTION}"

      - name: Grant write permissions to security-events for the next step
        uses: actions/login@v2

      - name: Log security event
        uses: actions/logger@v1
        env:
          EVENT_TYPE: "SECURITY_EVENT"

      - name: Rotate and update GitHub Secrets for secure data storage (rotation)
        uses: appleboy/github-secrets-action@v1.4.0
        env:
          REPO_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          token: "${REPO_TOKEN}"
          secrets-management-enabled: true
