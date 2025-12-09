#!/bin/bash

# Ensure the script is run as root (or with equivalent privileges)
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root." >&2
    exit 1
fi

# Define log directory and log file name
LOG_DIR="/var/logs"
LOG_FILE="$LOG_DIR/log_cleanup.log"

# Rotate logs older than 7 days, keeping at most 10 rotated logs
find "$LOG_DIR" -name "log_cleanup.log.*" -mtime +7 -exec rm {} \;
if [ $(ls -l "$LOG_DIR"/log_cleanup.log.* | wc -l) -ge 10 ]; then
    oldest=$(ls -t "$LOG_DIR"/log_cleanup.log.* | tail -n 1)
    rm "$oldest"
fi

# Log the start of the operation to a rotated log file or a new one if it doesn't exist
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
fi
logger -t log_cleanup "Starting to clean up old log files and compress current ones in $LOG_DIR" >> "$LOG_FILE" 2>&1

# Find and delete all .log files older than 7 days within the LOG_DIR, optimizing with maxdepth
find "$LOG_DIR" -maxdepth 1 -type f -name "*.log" -mtime +7 -delete || { echo "Failed to delete log files" >> "$LOG_FILE"; exit 1; }
logger -t log_cleanup "Deleted old log files from $LOG_DIR" >> "$LOG_FILE" 2>&1

# Compress the remaining .log files in the same directory, and log this action as well
tar -czvf logs_$(date +"%Y%m%d").tar.gz "$LOG_DIR"/*.log || { echo "Failed to compress log files" >> "$LOG_FILE"; exit 1; }
logger -t log_cleanup "Compressed remaining log files in $LOG_DIR" >> "$LOG_FILE" 2>&1
