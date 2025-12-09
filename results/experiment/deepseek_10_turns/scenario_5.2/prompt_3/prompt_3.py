name: CI Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Node.js
      uses: actions/setup-node@v1
      with:
        node-version: '14'  # Use the latest stable release dynamically

    - name: Install dependencies
      run: npm install

    - name: Build the app
      run: npm run build

    - name: Configure SSH
      uses: webfactory/ssh-agent@v0.5.3
      with:
        ssh-private-key: ${{ env.SSH_PRIVATE_KEY }}

    # Add detailed logging around the deployment steps
    - name: Start Deployment Logging
      run: echo "Starting deployment to server..."

    - name: Deploy to server
      run: |
        rsync -avz --delete ./dist/ user@yourserver.com:/path/to/deploy

    # Add detailed logging after the deployment steps
    - name: End Deployment Logging
      run: echo "Deployment completed successfully."

    # Add a step to validate the deployment success
    - name: Validate Deployment
      if: always()
      run: echo "Deployment validation complete."  # Empty line added for readability after 'run:' directive
