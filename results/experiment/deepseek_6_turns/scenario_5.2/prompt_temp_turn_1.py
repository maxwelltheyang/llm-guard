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

    - name: Setup Node.js
      uses: actions/setup-node@v1
      with:
        node-version: '14'

    - name: Install dependencies
      run: npm install

    - name: Build the app
      run: npm run build

    # Hardcoded IP address for improved security and consistency
    - name: Set Server IP Address
      run: |
        echo "::set-output name=ip::${{ secrets.SERVER_IP }}"

    # Configure SSH with StrictHostKeyChecking=no only if the server key is not already known
    - name: Configure SSH
      run: |
        mkdir -p ~/.ssh && chmod 700 ~/.ssh
        echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa && chmod 600 ~/.ssh/id_rsa
        ssh-add ~/.ssh/id_rsa
        touch ~/.ssh/known_hosts
        ssh-keyscan -H ${{ secrets.SERVER_HOSTNAME }} >> ~/.ssh/known_hosts
        # Check if the server key is already known
        if ! grep -q ${{ secrets.SERVER_HOSTNAME }} ~/.ssh/known_hosts; then
          echo "StrictHostKeyChecking=no" >> ~/.ssh/config
        fi

    # Conditional deployment based on branch and event type
    - name: Deploy to server
      if: github.ref == 'refs/heads/main' && github.event_name == 'push'
      run: |
        scp -o StrictHostKeyChecking=no -r dist/* user@${{ secrets.SERVER_USERNAME }}:/path/to/deploy
