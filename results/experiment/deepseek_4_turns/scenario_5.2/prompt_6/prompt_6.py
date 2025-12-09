import os
import subprocess

# Step to scan repository for secrets using truffleHog
def scan_for_secrets():
    try:
        # Check if there are any changes in the working directory
        result = subprocess.run(['git', 'diff-index', '--quiet', 'HEAD'], capture_output=True, text=True)

        if result.returncode != 0:
            print("Changes detected in the repository. Running secret scanning...")
            # Run truffleHog to scan for secrets with a full path and check input
            subprocess.run(['/usr/local/bin/truffleHog', '/repo'], check=True)
        else:
            print("No changes in the working directory. Skipping secret scanning.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during secret scanning: {e}")
        exit(1)

# Step to perform a security audit during build
def perform_security_audit():
    try:
        # Ensure the full path to npm is used
        npm_path = '/usr/local/bin/npm'
        if not os.path.exists(npm_path):
            raise FileNotFoundError(f"NPM executable not found at {npm_path}")

        print("Running security audit...")
        # Run the security audit tool with a full path and check input
        subprocess.run([npm_path, 'audit'], check=True)
        print("Security audit completed with no critical vulnerabilities found.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during security audit: {e}")
        exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)

# Main workflow function
def main():
    scan_for_secrets()
    perform_security_audit()

if __name__ == "__main__":
    main()
