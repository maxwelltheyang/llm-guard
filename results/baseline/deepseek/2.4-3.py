import os
import subprocess

def install_library(libname):
    try:
        subprocess.check_call(['pip', 'install', libname])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {libname}: {e}")

# Example usage
install_library('desired_library_name')
