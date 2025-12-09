#!/bin/bash

# Path to log directory
LOG_DIR="/var/logs/"

# Script log for its own activities
SCRIPT_LOG="/var/logs/manage_logs_script.log"

# Log for cleanup actions
CLEANUP_LOG="/var/log/cleanup.log"

# Ensure the script log and cleanup log files exist
touch "$SCRIPT_LOG" "$CLEANUP_LOG"

# Log function for both script and cleanup logs
log_message() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" | tee -a "$SCRIPT_LOG" >> "$CLEANUP_LOG"
}

# Function to rotate the cleanup log if it grows beyond 1MB
rotate_cleanup_log() {
    if [ "$(du -k "$CLEANUP_LOG" | cut -f1)" -ge 1024 ]; then
        mv "$CLEANUP_LOG" "$CLEANUP_LOG.old"
        touch "$CLEANUP_LOG"
        log_message "Rotated the cleanup log."
    fi
}

# Check if the script is running with root privileges, re-run with sudo if not
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

# Rotate the cleanup log if necessary
rotate_cleanup_log

# Acquire a lock to prevent concurrent executions
exec 9>/var/lock/manage_logs_script.lock
flock -n 9 || { log_message "Another instance of the script is already running."; exit 1; }

# Ensure important logs are backed up
BACKUP_DIR="/var/backups/logs"
mkdir -p "$BACKUP_DIR"

# Back up and verify logs
find "$LOG_DIR" -maxdepth 1 -type f -name '*.log' -mtime +7 -print -exec cp --preserve=mode,ownership,timestamps {} "$BACKUP_DIR" \; 2>>"$SCRIPT_LOG" | tee -a "$CLEANUP_LOG"
check_error "Failed to backup old .log files."

# Verify backup by comparing file counts
ORIG_FILE_COUNT=$(find "$LOG_DIR" -maxdepth 1 -type f -name '*.log' -mtime +7 | wc -l)
BACKUP_FILE_COUNT=$(find "$BACKUP_DIR" -maxdepth 1 -type f -name '*.log' -mtime +7 | wc -l)

if [ "$ORIG_FILE_COUNT" -ne "$BACKUP_FILE_COUNT" ]; then
    log_message "Backup verification failed. Aborting deletion process."
    exit 1
fi

# Prompt user for confirmation before deletion
read -p "Are you sure you want to delete log files older than 7 days (y/n)? " confirm
if [ "$confirm" != "y" ]; then
    log_message "Deletion process aborted by the user."
    echo "Deletion process aborted."
    exit 0
fi

# Find and delete .log files older than 7 days in the specified directory only
find "$LOG_DIR" -maxdepth 1 -type f -name '*.log' -mtime +7 -print -exec rm -f {} \; 2>>"$SCRIPT_LOG" | tee -a "$CLEANUP_LOG"
check_error "Failed to delete old .log files."

# Find current .log files and compress them
find "$LOG_DIR" -maxdepth 1 -type f -name '*.log' -mtime -7 -print -exec gzip -f {} \; 2>>"$SCRIPT_LOG" | tee -a "$CLEANUP_LOG"
check_error "Failed to compress current .log files."

log_message "Log management script executed successfully."

# Release lock
flock -u 9

# Secure the script permissions
chmod 700 "$0"
