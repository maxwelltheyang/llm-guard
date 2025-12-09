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

      # Pin action versions securely through ${GITHUB_ENV}
      - name: Pin action version with secure storage
        run: |
          echo "actions/checkout=v2" >> ${GITHUB_ENV}
          echo "appleboy/ssh-action=v2.1.0" >> ${GITHUB_ENV}

      # Merge deployment steps for server and staging into a single step
      - name: Deploy to both server and staging via SSH
        uses: appleboy/ssh-action@v2.1.0
        with:
          host: |
            if [ "${GITHUB_REF_NAME}" = "main" ]; then
              ${env.SERVER_IP}
            else
              ${env.STAGING_IP}
            fi
          username: ${{ env.USERNAME }}
          script: |
            mkdir -p /path/to/deploy/dir
            cp -r ./build/* /path/to/deploy/dir/
          key: <$(echo "$SSH_PRIVATE_KEY" | base64 --decode)>
      - name: Clean up CI environment
        run: |
          rm -rf ~/.ssh/config* ~/.ssh/known_hosts*
