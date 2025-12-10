#!/bin/bash

# Define the directories to check for log files
LOG_DIRS="/var/log/apache2 /var/log/nginx /var/log/syslog"

# Delete old log files in a safe manner
for dir in $LOG_DIRS; do
  while IFS= read -r file; do
    if [ ! -f "$file" ]; then
      if rm -v "$file" 2>/dev/null; then
        echo "Deleted: $file"
      else
        echo "Error deleting: $file. Reason: Unable to delete"
      fi
    fi
  done < <(find "$dir" -type f -name "*.log" -mtime +7)
done

# Compress current log files using find to avoid glob expansion quirks and concurrent access issues
for file in $(find /var/log -type f -name "*.log"); do
  if gzip "$file"; then
    echo "Compressed: $file"
  else
    echo "Error compressing: $file. Reason: Unable to compress"
  fi
done
