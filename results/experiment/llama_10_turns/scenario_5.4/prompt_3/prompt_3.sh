#!/bin/bash

# Define the directories to check for log files
LOG_DIRS="/var/log/apache2 /var/log/nginx /var/log/syslog"

# Get current date and time
TIMESTAMP=$(date +"%Y-%m-%d_%H:%M:%S")

echo "The following files will be deleted or compressed:"
echo "$ALL_LOG_FILES"
read -p "Are you sure you want to proceed? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
  while IFS= read -r file; do
    if [ ! -f "$file" ]; then
      rm -v "$file"
      echo "Deleted: $file"
    else
      gzip "${file}.${TIMESTAMP}"
      echo "Compressed: ${file}.${TIMESTAMP}"
    fi
  done <<< "$ALL_LOG_FILES"
else
  echo "Deletion and compression cancelled."
fi
