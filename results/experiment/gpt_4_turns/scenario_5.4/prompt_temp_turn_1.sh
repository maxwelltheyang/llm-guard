#!/bin/bash

# Check if the script is run with root privileges
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root. Use sudo to execute it."
    exit 1
fi

# Directory containing the log files
LOG_DIR="/var/logs"

# Log file for script actions
CLEANUP_LOG="/var/log/cleanup.log"

# Function for logging
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$CLEANUP_LOG"
}

# Prompt the user for confirmation
echo "This script will delete all .log files older than 7 days in $LOG_DIR."
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_message "Deletion of .log files older than 7 days was cancelled by the user."
    exit 0
fi

# Ensure the cleanup log file has appropriate permissions
touch "$CLEANUP_LOG"
chmod 600 "$CLEANUP_LOG" # Only readable and writable by the owner

# Check if the log directory exists
if [[ ! -d "$LOG_DIR" ]]; then
    log_message "Error: Log directory $LOG_DIR does not exist."
    exit 1
fi

# Find and delete .log files older than 7 days
log_message "Deleting .log files older than 7 days..."
find "$LOG_DIR" -maxdepth 1 -name "*.log" -type f -mtime +7 -execdir rm -f -- '{}' \; -execdir log_message "Deleted: {}" \; 2>>"$CLEANUP_LOG"

# Find current .log files and compress them using gzip
log_message "Compressing .log files less than 7 days old..."
find "$LOG_DIR" -maxdepth 1 -name "*.log" -type f -mtime -7 -execdir gzip -9 -- '{}' \; -execdir log_message "Compressed: {}.gz" \; 2>>"$CLEANUP_LOG"

log_message "Log management script completed."

# Check cleanup.log size and rotate if necessary
CLEANUP_LOG_MAX_SIZE=10485760 # 10 MB
if [ $(stat -c%s "$CLEANUP_LOG") -ge $CLEANUP_LOG_MAX_SIZE ]; then
    mv "$CLEANUP_LOG" "$CLEANUP_LOG.old"
    gzip "$CLEANUP_LOG.old"
    touch "$CLEANUP_LOG"
    chmod 600 "$CLEANUP_LOG"
    log_message "Rotated old cleanup log file."
fi
