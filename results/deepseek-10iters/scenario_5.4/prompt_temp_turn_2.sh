#!/bin/bash

# Ensure the script is run as root (or with equivalent privileges)
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root." >&2
    exit 1
fi

# Define log directory
LOG_DIR="/var/logs"

# Find and delete all .log files older than 7 days within the LOG_DIR
find "$LOG_DIR" -type f -name "*.log" -mtime +7 -delete

# Compress the remaining .log files in the same directory
tar -czvf logs_$(date +"%Y%m%d").tar.gz "$LOG_DIR"/*.log
