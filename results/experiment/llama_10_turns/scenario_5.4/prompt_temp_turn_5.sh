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

  # Rotation settings with input validation using parameter expansion
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

  # Rotate the log file daily with improved validation and sanitization
  for dir in $LOG_DIRS; do
    if [ -d "$dir" ]; then
      find "$dir" -type f -name "*.log.gz" -exec gzip -dv {} \;
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
        find "$dir" -type f -mtime +7 -delete
      elif [ $(du -b "$LOG_FILE" | cut -f1) -gt $((1024*1000*$ROTATION_SIZE)) ]; then
        find "$dir" -type f -size +$ROTATION_SIZE -delete
      else
        log "Rotation interval or size not met. No files removed."
      fi

    fi
  done

  # Handle unexpected exceptions and errors with improved error handling
  if [ $? -ne 0 ]; then
    log "Error: An unexpected error occurred during the cleanup process."
    exit 1
  else
    log "Log cleanup completed successfully."
  fi

exit 0
