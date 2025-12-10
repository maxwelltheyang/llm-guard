#!/bin/bash

# Define the directories to check for log files
LOG_DIRS="/var/log/apache2 /var/log/nginx /var/log/syslog"

# Run the find command with sudo to get a list of old log files and current log files
ALL_LOG_FILES=$(sudo find "/var/log" -type f -name "*.log")

# Delete old log files in a safe manner
while IFS= read -r file; do
  if [ ! -f "$file" ]; then
    rm -v "$file"
    echo "Deleted: $file"
  else
    gzip "$file"
    echo "Compressed: $file"
  fi
done <<< "$ALL_LOG_FILES"
