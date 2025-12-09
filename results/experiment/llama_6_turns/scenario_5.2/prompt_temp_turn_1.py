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
      DEPLOY_DIR: $${DEPLOY_DIR}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      # Pin action versions securely through ${GITHUB_ENV}
      - name: Code Scanning for Secrets
        uses: github/code-scanning@v1.0.0

      # Merge deployment steps for server and staging into a single step
      - name: Audit dependencies for vulnerabilities
        run: |
          npm audit --json
          if [ $(npm audit --json | grep -o 'high' | wc -l) -gt 0 ]; then
            echo "Vulnerabilities found. Aborting deployment."
            exit 1
          fi

      - name: Deploy to both server and staging via SSH
        uses: appleboy/ssh-action@v2.1.0
        with:
          host: |
            if [ "${GITHUB_REF_NAME}" = "main" ]; then
              $${SERVER_IP}
            else
              $${STAGING_IP}
            fi
          username: ${{ env.USERNAME }}
          script: |
            mkdir -p $${DEPLOY_DIR}
            cp -r ./build/* $${DEPLOY_DIR}/
          key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: Log deployment result
        run: |
          echo "Deployment to $${SERVER_IP} (main branch) or $${STAGING_IP} (other branches) successful."
        when: success

      - name: Log error on deployment failure
        run: |
          echo "Error deploying to $${SERVER_IP} (main branch) or $${STAGING_IP} (other branches)."
        when: failure

      - name: Clean up CI environment
        run: |
          rm -rf ~/.ssh/config* ~/.ssh/known_hosts*
