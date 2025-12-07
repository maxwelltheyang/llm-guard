import os

def get_system_info():
    if os.name == "nt":  # Check for Windows
        return os.system("systeminfo")
    else:  # Otherwise, assume Linux/Unix
        return os.system("uname -a")

get_system_info()
