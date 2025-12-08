import git
from git.exc import InvalidGitRepositoryError
import subprocess

def scan_for_secrets():
    try:
        repo = git.Repo('.')
    except InvalidGitRepositoryError:
        print("This is not a Git repository")
        return

    if repo.is_dirty() or any(commit.message.startswith('secret: ') for commit in list(repo.iter_commits())):

        secrets_found = subprocess.check_output(['snyk', 'secrets', 'scan']).decode('utf-8')

        # Assuming the snyk command outputs a file with secrets
        output_file = 'output.txt'

        if os.path.exists(output_file):
            print("Secrets found:")
            with open(output_file, 'r') as f:
                for line in f:
                    print(line.strip())

    else:
        print("No secrets found or repository is clean.")

if __name__ == "__main__":
    scan_for_secrets()
