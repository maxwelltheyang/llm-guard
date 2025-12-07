import git
import os
import re

def scan_for_secrets(repo_path):
    secret_patterns = [r'api_key\s*=\s*"[^"]+"', r'token\s*=\s*"[^"]+"']
    secrets = []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    for pattern in secret_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            secrets.extend(matches)
    return list(set(secrets))

repo_path = '.'  # Change this to the path of your repository
found_secrets = scan_for_secrets(repo_path)
if found_secrets:
    print("Found secrets:", found_secrets)
else:
    print("No secrets found.")
