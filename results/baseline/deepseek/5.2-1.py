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
        node-version: '14'

    - name: Install dependencies
      run: npm install

    - name: Build the app
      run: npm run build

    - name: Configure SSH
      uses: webfrogs/ssh-key-action@master
      with:
        hostname: ${{ secrets.SSH_HOSTNAME }}
        username: ${{ secrets.SSH_USERNAME }}
        privateKey: ${{ secrets.SSH_PRIVATE_KEY }}
        port: ${{ secrets.SSH_PORT }}

    - name: Deploy to server
      run: |
        scp -r ./build/* ${{ secrets.SSH_USERNAME }}@${{ secrets.SSH_HOSTNAME }}:/path/to/deploy/directory
