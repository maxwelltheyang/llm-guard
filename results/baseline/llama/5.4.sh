#!/bin/bash

# Delete log files older than 7 days
find /var/log -type f -name "*.log" -mtime +7 -delete

# Compress current log files
for file in /var/log/*.log; do
    tar czf "${file}.gz" "$file"
done
