#!/bin/bash

# Define the log directory and ensure it exists with proper permissions
LOG_DIR="/var/logs"
if [ -d "$LOG_DIR" ]; then
    # Find all .log files older than 7 days and delete them, ensuring only .log files are deleted
    find "$LOG_DIR" -type f \( -name "*.log" \) -size +0c -print0 | xargs -0 rm
else
    echo "Log directory $LOG_DIR does not exist or is inaccessible." >&2
fi

# Compress current .log files with a safer method for generating filenames
current_date=$(date +"%Y%m%d")
tar -czvf logs_$current_date.tar.gz "$LOG_DIR"/*.log
