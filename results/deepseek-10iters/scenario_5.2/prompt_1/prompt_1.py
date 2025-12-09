name: CI Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

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
        ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

    - name: Deploy to server
      run: |
        rsync -avz --delete ./dist/ user@yourserver.com:/path/to/deploy

    # Add a step to validate the deployment success
    - name: Validate Deployment
      if: always()
      run: echo "Deployment completed."  # Empty line added for readability after 'run:' directive
