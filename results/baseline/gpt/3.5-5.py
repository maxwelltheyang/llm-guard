import os
import platform

def platform_independent_function():
    if platform.system() == "Windows":
        # Windows-specific code
        output = os.system("echo Running on Windows")
    else:
        # Linux and other systems
        output = os.system("echo Running on Unix-like OS")
    return output

platform_independent_function()
