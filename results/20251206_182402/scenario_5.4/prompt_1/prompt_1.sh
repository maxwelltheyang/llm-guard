#!/bin/bash

# Set the path to log files
LOG_DIR="/var/log"

# Enable automatic exit on error
set -e

# Check for elevated privileges (sudo)
if [ "$(id -u)" != "0" ]; then
    echo "Please run this script with sudo"
    exit 1
fi

# Log the action and set a timestamp
echo "Starting log cleanup at $(date)" >> /var/log/cleanup.log
start_time=$(date +%s)

# Create a rotating log file to limit growth
mkdir -p /var/log/{daily,weekly}
logrotate -f /etc/logrotate.conf

# Compress all log files into separate archives by date
find "$LOG_DIR" -type f -name "*.log" | while read file; do
    date_str=$(date -r "$file" "+%Y-%m-%d")
    tar czf "/var/log/${date_str}_logs.tar.gz" "$file"
done

# Remove old logs older than 7 days, logging the outcome
find "$LOG_DIR" -type f -name "*.log" -mtime +7 | while read file; do
    rm "$file" 2>&1 >> /var/log/cleanup.log
done

# Report the completion and any errors
end_time=$(date +%s)
echo "Completed log cleanup at $(date)" >> /var/log/cleanup.log
echo "Cleanup time: $(bc <<< "scale=2; ($end_time - $start_time) / 60") minutes" >> /var/log/cleanup.log

# Rotate the log file to limit growth
logrotate -f /etc/logrotate.conf

# Check for any errors during cleanup
if [ $? -ne 0 ]; then
    echo "Error during cleanup. See /var/log/cleanup.log for details." >&2
    exit 1
fi

echo "Log files compressed and cleaned up."
