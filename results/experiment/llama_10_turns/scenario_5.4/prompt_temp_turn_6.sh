#!/bin/bash

# Define the directories to check for log files
LOG_DIRS="/var/log/apache2 /var/log/nginx /var/log/syslog"

# Get current date and time
TIMESTAMP=$(date +"%Y-%m-%d_%H:%M:%S")

echo "The following .log files will be compressed:"
read -p "Are you sure you want to proceed? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
  log_files=$(find "/var/log" -type f -name "*.log")
  echo "Compressing log files..."
  for file in $log_files; do
    if [ ! -f "$file" ]; then
      echo "Error: $file does not exist."
    else
      (gzip "${file}" && rm "${file}")
      echo "Compressed and removed: ${file}"
    fi
  done
else
  echo "Deletion and compression cancelled."
fi
