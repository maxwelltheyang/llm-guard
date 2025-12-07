import subprocess

def run_audit():
    try:
        result = subprocess.run(['npm', 'audit'], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Audit failed: {e.stderr}")

if __name__ == "__main__":
    run_audit()
