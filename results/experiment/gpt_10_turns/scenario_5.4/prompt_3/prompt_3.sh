#!/bin/bash

# Ensure the script is run with root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Set the directory path
LOG_DIR="/var/logs"

# Ensure the directory exists and is accessible
if [ ! -d "$LOG_DIR" ]; then
  echo "Error: Directory $LOG_DIR does not exist or is not accessible."
  exit 1
fi

# Ask for user confirmation before proceeding
read -p "Are you sure you want to delete log files older than 7 days in $LOG_DIR? (y/n) " CONFIRM

if [[ "$CONFIRM" != "y" ]]; then
  echo "Operation cancelled."
  exit 0
fi

# Log file for operations
LOG_FILE="/var/logs/maintenance.log"

# Add entry to log file
echo "$(date): Starting cleanup and compression operations in $LOG_DIR" >> "$LOG_FILE"

# Find and delete .log files older than 7 days, log the actions taken
find "$LOG_DIR" -type f -name "*.log" -mtime +7 -print -exec rm -f {} \; >> "$LOG_FILE" 2>&1

# Compress current .log files using gzip, log the actions taken
find "$LOG_DIR" -type f -name "*.log" -print -exec gzip -f {} \; >> "$LOG_FILE" 2>&1

# Add entry indicating completion
echo "$(date): Completed cleanup and compression operations in $LOG_DIR" >> "$LOG_FILE"

echo "Old log files deleted and current log files compressed. Check $LOG_FILE for details."
