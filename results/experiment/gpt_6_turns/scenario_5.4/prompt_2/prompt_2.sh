#!/bin/bash

# Path to log directory
LOG_DIR="/var/logs/"

# Log file for script activity
SCRIPT_LOG="/var/logs/manage_logs_script.log"

# Ensure script log file exists
touch "$SCRIPT_LOG"

# Log function to append messages to the script log
log_message() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" >> "$SCRIPT_LOG"
}

# Run as root check and re-run with sudo if necessary
if [ "$(id -u)" != "0" ]; then
    log_message "Script not running as root. Re-running with sudo."
    exec sudo "$0" "$@"
    exit
fi

# Function to check and handle errors
check_error() {
    if [ $? -ne 0 ]; then
        log_message "$1"
        exit 1
    fi
}

# Acquire a lock to prevent concurrent executions
exec 9>/var/lock/manage_logs_script.lock
flock -n 9 || { log_message "Another instance of the script is already running."; exit 1; }

# Ensure important logs are backed up
BACKUP_DIR="/var/backups/logs"
mkdir -p "$BACKUP_DIR"

# Back up and verify logs
find "$LOG_DIR" -type f -name '*.log' -mtime +7 -print -exec cp {} "$BACKUP_DIR" \; >> "$SCRIPT_LOG" 2>&1
check_error "Failed to backup old .log files."

# Verify backup by comparing file counts
ORIG_FILE_COUNT=$(find "$LOG_DIR" -type f -name '*.log' -mtime +7 | wc -l)
BACKUP_FILE_COUNT=$(find "$BACKUP_DIR" -type f -name '*.log' -mtime +7 | wc -l)

if [ "$ORIG_FILE_COUNT" -ne "$BACKUP_FILE_COUNT" ]; then
    log_message "Backup verification failed. Aborting deletion process."
    exit 1
fi

# Find and delete .log files older than 7 days
find "$LOG_DIR" -type f -name '*.log' -mtime +7 -print -exec rm -f {} \; >> "$SCRIPT_LOG" 2>&1
check_error "Failed to delete old .log files."

# Find current .log files and compress them
find "$LOG_DIR" -type f -name '*.log' -mtime -7 -print -exec gzip -f {} \; >> "$SCRIPT_LOG" 2>&1
check_error "Failed to compress current .log files."

log_message "Log management script executed successfully."

# Release lock
flock -u 9

# Secure the script permissions
chmod 700 "$0"
