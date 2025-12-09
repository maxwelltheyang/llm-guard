#!/bin/bash

# Ensure the script is run as root (or with equivalent privileges)
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root." >&2
    exit 1
fi

# Define log directory
LOG_DIR="/var/logs"

# Log the start of the operation
logger -t log_cleanup "Starting to clean up old log files and compress current ones in $LOG_DIR"

# Find and delete all .log files older than 7 days within the LOG_DIR, optimizing with maxdepth
find "$LOG_DIR" -maxdepth 1 -type f -name "*.log" -mtime +7 -delete

# Log that old log files have been deleted
logger -t log_cleanup "Deleted old log files from $LOG_DIR"

# Compress the remaining .log files in the same directory, and log this action as well
tar -czvf logs_$(date +"%Y%m%d").tar.gz "$LOG_DIR"/*.log
logger -t log_cleanup "Compressed remaining log files in $LOG_DIR"
