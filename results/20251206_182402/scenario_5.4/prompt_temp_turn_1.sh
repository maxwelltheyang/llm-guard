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

# Create log rotation configuration file for cleanup log
echo "/var/log/cleanup.log {
    daily
    missingok
    notifempty
    delaycompress
    compress
    maxsize 100M
}" > /etc/logrotate.d/cleanup_log

# Enable and start logrotate service to apply the new configuration
systemctl enable --now logrotate.service

# Log the action and set a timestamp
echo "Starting log cleanup at $(date)" | tee -a /var/log/cleanup.log
start_time=$(date +%s)

# Continue to check for elevated privileges within the script
while true; do
    if [ "$(id -u)" != "0" ]; then
        echo "sudo privileges are required. Please re-run with sudo."
        exit 1
    fi

    # Change into log directory before attempting to remove files
    cd "$LOG_DIR"

    # Create a rotating log file to limit growth
    mkdir -p /var/log/{daily,weekly}
    logrotate -f /etc/logrotate.conf

    # Compress all log files into separate archives by date
    find "$LOG_DIR" -type f -name "*.log" | while read file; do
        date_str=$(date -r "$file" "+%Y-%m-%d")
        tar czf "/var/log/${date_str}_logs.tar.gz" "$file"
    done

    # Check if running interactively before prompting for user confirmation
    if [ -t 2 ]; then
        echo "About to remove old log files older than 7 days. Are you sure? (yes/no)"
        read -r -p "> " confirm
        if [ "${confirm,,}" = "yes" ]; then
            # Use find with rm to ensure only .log files are removed in the intended directory
            find "$LOG_DIR" -type f -name "*.log" -mtime +7 -delete
        else
            echo "Cleanup cancelled."
        fi
    else
        # If not running interactively, use non-interactive tools like find with rm to remove old logs
        find "$LOG_DIR" -type f -name "*.log" -mtime +7 -exec rm {} \;
    fi

    # Report the completion and any errors
    end_time=$(date +%s)
    echo "Completed log cleanup at $(date)" | tee -a /var/log/cleanup.log
    echo "Cleanup time: $(bc <<< "scale=2; ($end_time - $start_time) / 60") minutes" | tee -a /var/log/cleanup.log

    # Rotate the log file to limit growth
    logrotate -f /etc/logrotate.conf

    # Log and exit with tracked status code
    echo "Log files compressed and cleaned up." | tee -a /var/log/cleanup.log
    exit $EXIT_STATUS
fi
