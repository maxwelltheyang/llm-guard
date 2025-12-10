#!/bin/bash

# Define the directories to check for log files with path validation
LOG_DIRS="/var/log/apache2 /var/log/nginx /var/log/syslog"
VALID_LOG_DIRS=$(echo "$LOG_DIRS" | tr ' ' '\n' | sort -u)

for dir in $(echo "$VALID_LOG_DIRS"); do
  if [ ! -d "$dir" ]; then
    echo "Error: $dir is not a valid directory."
    exit 1
  fi

  # Get current date and time
  TIMESTAMP=$(date +"%Y-%m-%d_%H:%M:%S")

  # Configure logging
  LOG_FILE="/var/log/cleanup.log"
  LOG_LEVEL="INFO"

  # Rotation settings with input validation
  if [ -n "${ROTATION_INTERVAL_ENV}" ]; then
    ROTATION_INTERVAL=${ROTATION_INTERVAL_ENV}
    if ! [[ $ROTATION_INTERVAL =~ ^[0-9]+$ ]]; then
      echo "Error: Invalid integer value for rotation interval."
      exit 1
    fi
  else
    ROTATION_INTERVAL=${ROTATION_INTERVAL:-7} # days
  fi

  if [ -n "${ROTATION_SIZE_ENV}" ]; then
    ROTATION_SIZE=${ROTATION_SIZE_ENV}
    if ! [[ $ROTATION_SIZE =~ ^[0-9]+(.[0-9]+)?$ ]]; then
      echo "Error: Invalid value for rotation size."
      exit 1
    fi
  else
    ROTATION_SIZE=${ROTATION_SIZE:-1000M} # max size before rotation in MB
  fi

  function log() {
    echo "$(date +"%Y-%m-%d_%H:%M:%S") - $LOG_LEVEL: $1" >> "$LOG_FILE"
  }

  # Check if user has sufficient permissions to remove log files
  SUFFICIENT_PERMISSIONS=true
  for file in $(find "/var/log" -type f -name "*.log"); do
    if [ ! -w "$(dirname "$file")" ]; then
      log "Error: Permission denied when removing old log files."
      SUFFICIENT_PERMISSIONS=false
    fi
  done

  # Rotate the log file daily
  find "$LOG_FILE" -type f -print0 | xargs -0 -I {} gzip
  gzip -d "$LOG_FILE.gz"

  if $SUFFICIENT_PERMISSIONS; then
    # Remove old log files based on rotation interval or size
    while true; do
      read -p "Do you want to remove the original log file after compression? (yes/no): " choice
      case "$choice" in
        yes) break ;;
        no) echo "Log cleanup cancelled."
             exit 0 ;;
        *) echo "Invalid input. Please choose 'yes' or 'no'."
           continue ;;
      esac
    done

    if [ $(date +%s) -gt $(date -d "-$ROTATION_INTERVAL days" +%s) ]; then
      find "$LOG_FILE"* -type f -mtime +7 -delete
    elif [ $(du -b "$LOG_FILE" | cut -f1) -gt $((1024*1000*$ROTATION_SIZE)) ]; then
      find "$LOG_FILE"* -type f -size +$ROTATION_SIZE -delete
    else
      log "Rotation interval or size not met. No files removed."
    fi

  else
    echo "Permission denied when removing old log files. Check user permissions."
    exit 1
  fi

  # Handle unexpected exceptions and errors
  if [ $? -ne 0 ]; then
    log "Error: An error occurred during the cleanup process."
    exit 1
  fi

echo "Log cleanup completed successfully."
exit 0
