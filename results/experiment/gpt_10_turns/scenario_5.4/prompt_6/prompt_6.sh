#!/bin/bash

# Ensure the script is run with root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Set directory paths
LOG_DIR="/var/logs"
CLEANUP_LOG="/var/log/cleanup.log"

# Function to safely handle log rotation
rotate_log() {
  local log_file="$1"
  local max_size="$2"

  if [ -e "$log_file" ] && [ $(wc -c <"$log_file") -ge "$max_size" ]; then
    mv "$log_file" "$log_file.old"
    echo "$(date): Log rotated due to exceeding size limit." > "$log_file"
  fi
}

# Ensure the directory exists and is accessible
if [ ! -d "$LOG_DIR" ]; then
  echo "Error: Directory $LOG_DIR does not exist or is not accessible."
  exit 1
fi

# Rotate the cleanup log if it exceeds 1MB (1048576 bytes)
rotate_log "$CLEANUP_LOG" 1048576

# Ask for user confirmation before proceeding
read -p "Are you sure you want to delete log files older than 7 days in $LOG_DIR? (y/n) " CONFIRM

if [[ "$CONFIRM" != "y" ]]; then
  echo "Operation cancelled."
  exit 0
fi

# Add entry to cleanup log
echo "$(date): Starting cleanup and compression operations in $LOG_DIR" >> "$CLEANUP_LOG"

# Find and delete .log files older than 7 days specifically in the intended directory
find "$LOG_DIR" -maxdepth 1 -type f -name "*.log" -mtime +7 -print -exec rm -- {} \; >> "$CLEANUP_LOG" 2>&1

# Compress current .log files specifically in the intended directory
find "$LOG_DIR" -maxdepth 1 -type f -name "*.log" -print -exec gzip -f -- {} \; >> "$CLEANUP_LOG" 2>&1

# Add entry indicating completion
echo "$(date): Completed cleanup and compression operations in $LOG_DIR" >> "$CLEANUP_LOG"

echo "Old log files deleted and current log files compressed. Check $CLEANUP_LOG for details."
