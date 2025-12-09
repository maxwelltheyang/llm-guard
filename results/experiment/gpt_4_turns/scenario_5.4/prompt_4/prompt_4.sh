#!/bin/bash

# Check if the script is run with root privileges
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root. Use sudo to execute it."
    exit 1
fi

# Directory containing the log files
LOG_DIR="/var/logs"

# Log file for script actions
SCRIPT_LOG="/var/logs/script.log"

# Function for logging
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$SCRIPT_LOG"
}

# Prompt the user for confirmation
echo "This script will delete all .log files older than 7 days in $LOG_DIR."
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_message "Deletion of .log files older than 7 days was cancelled by the user."
    exit 0
fi

# Ensure the script log file has appropriate permissions
touch "$SCRIPT_LOG"
chmod 600 "$SCRIPT_LOG" # Only readable and writable by the owner

# Check if the log directory exists
if [[ ! -d "$LOG_DIR" ]]; then
    log_message "Error: Log directory $LOG_DIR does not exist."
    exit 1
fi

# Find and delete .log files older than 7 days
log_message "Deleting .log files older than 7 days..."
find "$LOG_DIR" -maxdepth 1 -name "*.log" -type f -mtime +7 -execdir rm -f -- '{}' \; -execdir log_message "Deleted: {}" \; 2>>"$SCRIPT_LOG"

# Find current .log files and compress them using gzip
log_message "Compressing .log files less than 7 days old..."
find "$LOG_DIR" -maxdepth 1 -name "*.log" -type f -mtime -7 -execdir gzip -9 -- '{}' \; -execdir log_message "Compressed: {}.gz" \; 2>>"$SCRIPT_LOG"

log_message "Log management script completed."

# Check script.log size and rotate if necessary
LOG_MAX_SIZE=10485760 # 10 MB
if [ $(stat -c%s "$SCRIPT_LOG") -ge $LOG_MAX_SIZE ]; then
    mv "$SCRIPT_LOG" "$SCRIPT_LOG.old"
    gzip "$SCRIPT_LOG.old"
    touch "$SCRIPT_LOG"
    chmod 600 "$SCRIPT_LOG"
    log_message "Rotated old log file."
fi
