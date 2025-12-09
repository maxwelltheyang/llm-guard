#!/bin/bash

# Define the log directory
LOG_DIR="/var/logs/"

# Find and delete log files older than 7 days
find "$LOG_DIR" -type f -name "*.log" -mtime +7 -exec rm {} \;

# Compress current .log files
for file in $LOG_DIR*.log; do
  if [ -f "$file" ]; then
    gzip -9 "$file"
  fi
done

echo "Log cleaning and compression completed."
