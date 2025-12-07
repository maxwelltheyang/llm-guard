import os
import subprocess
from datetime import datetime

# Get the current branch and commit hash
branch = os.environ.get('GITHUB_BRANCH')
commit_hash = os.environ.get('GITHUB_SHA')

# Set up the GitHub API token as an environment variable
github_token = os.environ.get('GITHUB_TOKEN')

# Define a function to create a new tag with the format 'vX.Y.Z' based on the commit hash
def create_tag(commit_hash):
    version = datetime.now().strftime('%Y.%m.%d')
    return f"v{version}"

# Define a function to push tags to GitHub
def push_tags(tag_name, branch):
    subprocess.run([
        "git",
        "push",
        "--tags",
        f"origin {branch}:{tag_name}"
    ])

# Define a function to create and push tags based on the current commit hash
def create_and_push_tags():
    tag_name = create_tag(commit_hash)
    push_tags(tag_name, branch)

create_and_push_tags()
