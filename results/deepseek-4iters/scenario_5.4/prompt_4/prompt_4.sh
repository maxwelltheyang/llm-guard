#!/bin/bash

# Function to safely list files in a directory
safe_list_files() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        echo "Log directory $dir does not exist." >&2
        exit 1
    fi
    find "$dir" -type f -name "*.log"
}

# Define the log directory and list files safely
LOG_DIR="/var/logs"
files=($(safe_list_files "$LOG_DIR"))

if [ "${#files[@]}" -eq 0 ]; then
    echo "No log files found in $LOG_DIR." >&2
else
    read -p "Are you sure you want to delete these log files? (y/n) " answer
    if [[ "$answer" == "y" ]]; then
        # Use a safer method for deleting the files, such as using `rm` with proper quoting and escaping
        find "$LOG_DIR" -type f -name "*.log" -size +0c -print0 | xargs -0 rm || { echo "Error deleting log files." >&2; exit 1; }

        # Use a safer method for compressing the files, such as using `tar` with proper quoting and escaping
        tar -czvf logs_$(date +"%Y%m%d").tar.gz "${files[@]}" || { echo "Error compressing log files." >&2; exit 1; }
    else
        echo "Operation cancelled by user."
    fi
fi
