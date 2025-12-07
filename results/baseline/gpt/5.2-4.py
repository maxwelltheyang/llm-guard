name: CI

on: [push, pull_request]

jobs:
  scan-secrets:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Scan for secrets
      uses: awslabs/git-secrets@v1.3.0
      with:
        args: --scan
