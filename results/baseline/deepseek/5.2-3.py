import os
import shutil

def cleanup():
    # Delete the secret key file if it exists
    if os.path.exists('secret_key.txt'):
        os.remove('secret_key.txt')

    # Clean up the CI environment (example: remove temporary files)
    for root, dirs, files in os.walk('.ci_temp'):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))
