import os
import platform

def is_linux():
    return platform.system() == "Linux"

def is_windows():
    return platform.system() == "Windows"

# Your code here, making sure it works on both platforms
if is_linux():
    # Linux-specific code
    print("Running on Linux")
elif is_windows():
    # Windows-specific code
    print("Running on Windows")
else:
    print("Unsupported OS")
