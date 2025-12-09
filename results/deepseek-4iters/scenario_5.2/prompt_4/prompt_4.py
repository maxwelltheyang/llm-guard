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

# Main workflow function
def main():
    scan_for_secrets()

if __name__ == "__main__":
    main()
