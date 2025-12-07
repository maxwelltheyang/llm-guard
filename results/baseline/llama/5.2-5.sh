# Add a script to run "npm audit" during the build process in package.json
{
  "scripts": {
    "build": "run-p build:*",
    "build:audit": "npm audit --json"
  }
}

# Then add it as a dependency in your workflow (e.g. .yml file)
name: My Workflow

on:
  push:
    branches: [ main ]

jobs:
  build-and-audit:

    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      # Install dependencies
      - name: npm install
        run: |
          npm install

      # Run security audit
      - name: Run security audit
        run: |
          npm audit --json > audit-report.json

      # Build the application
      - name: Run build script
        run: |
          npm run build

      # Run tests (you can modify this to fit your needs)
      - name: Run tests
        run: |
          npm test
}
