#!/bin/bash

# Delete log files older than 7 days
find /var/logs/ -type f -name "*.log" -mtime +7 -delete

# Compress current log files
for file in /var/logs/*.log; do
  gzip -f "$file"
done
