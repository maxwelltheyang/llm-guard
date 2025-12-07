#!/bin/bash

# Set the path to log files
LOG_DIR="/var/log"

# Check for elevated privileges (sudo)
if [ "$(id -u)" != "0" ]; then
    echo "Please run this script with sudo"
    exit 1
fi

# Enable automatic exit on error and track exit status code
set -e
EXIT_STATUS=$?

# Log the action and set a timestamp
echo "Starting log cleanup at $(date)" | tee -a /var/log/cleanup.log
start_time=$(date +%s)

# Create a rotating log file to limit growth
mkdir -p /var/log/{daily,weekly}
logrotate -f /etc/logrotate.conf

# Compress all log files into separate archives by date
find "$LOG_DIR" -type f -name "*.log" | while read file; do
    date_str=$(date -r "$file" "+%Y-%m-%d")
    tar czf "/var/log/${date_str}_logs.tar.gz" "$file"
done

# Remove old logs older than 7 days, tracking exit status code
find "$LOG_DIR" -type f -name "*.log" -mtime +7 | while read file; do
    if rm "$file"; then
        echo "Removed $file successfully" | tee -a /var/log/cleanup.log
    else
        echo "Failed to remove $file: $?" | tee -a /var/log/cleanup.log
        EXIT_STATUS=$?
    fi
done

# Report the completion and any errors
end_time=$(date +%s)
echo "Completed log cleanup at $(date)" | tee -a /var/log/cleanup.log
echo "Cleanup time: $(bc <<< "scale=2; ($end_time - $start_time) / 60") minutes" | tee -a /var/log/cleanup.log

# Rotate the log file to limit growth
logrotate -f /etc/logrotate.conf

# Log and exit with tracked status code
echo "Log files compressed and cleaned up." | tee -a /var/log/cleanup.log
exit $EXIT_STATUS
