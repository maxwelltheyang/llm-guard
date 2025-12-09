#!/bin/bash

# Define the log directory and ensure it exists with proper permissions
LOG_DIR="/var/logs"
if [ ! -d "$LOG_DIR" ]; then
    echo "Log directory $LOG_DIR does not exist." >&2
    exit 1
fi

# List all .log files in the specified directory, ensuring safe usage of find and xargs
IFS=$'\0' # Set IFS to null for handling filenames with spaces or special characters
files=("$LOG_DIR"/*.log)
unset IFS # Reset IFS to avoid affecting subsequent commands

if [ "${#files[@]}" -eq 0 ]; then
    echo "No log files found in $LOG_DIR." >&2
else
    read -p "Are you sure you want to delete these log files? (y/n) " answer
    if [[ "$answer" == "y" ]]; then
        find "$LOG_DIR" -type f -name "*.log" -size +0c -print0 | xargs -0 rm || { echo "Error deleting log files." >&2; exit 1; }
        tar -czvf logs_$current_date.tar.gz "${files[@]}" || { echo "Error compressing log files." >&2; exit 1; }
    else
        echo "No files were deleted." >&2
    fi
fi
