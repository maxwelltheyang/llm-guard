#!/bin/bash

# Set the path to log files
LOG_DIR="/var/log"

# Check for elevated privileges (sudo)
if [ "$(id -u)" != "0" ]; then
    echo "Please run this script with sudo"
    exit 1
fi

EXIT_STATUS=0

# Create a backup of the original logrotate configuration file
cp /etc/logrotate.conf{,.backup}

try_logrotate() {
    logrotate -f /etc/logrotate.conf > /dev/null 2>&1 || echo "Failed to apply logrotate config"
}

# Attempt to create and enable logrotate configuration for cleanup log
echo "/var/log/cleanup.log {
daily
missingok
notifempty
delaycompress
compress
maxsize 100M
}" > /etc/logrotate.d/cleanup_log

if ! try_logrotate; then
    # If the config application fails, return the original logrotate.conf and exit with a meaningful status code
    mv "/etc/logrotate.conf.backup" "/etc/logrotate.conf"
    echo "Failed to create logrotate configuration. Restoring original file."
    EXIT_STATUS=1
fi

# Enable and start logrotate service to apply the new configuration
if ! systemctl enable --now logrotate.service; then
    echo "Failed to enable or start logrotate service."
    EXIT_STATUS=1
fi

# Log the action and set a timestamp
echo "Starting log cleanup at $(date)" | tee -a /var/log/cleanup.log
start_time=$(date +%s)

while true; do
    if [ "$(id -u)" != "0" ]; then
        echo "sudo privileges are required. Please re-run with sudo."
        exit $EXIT_STATUS
    fi

    cd "$LOG_DIR"

    # Create a rotating log file to limit growth
    mkdir -p /var/log/{daily,weekly}
    if ! logrotate -f /etc/logrotate.conf; then
        echo "Failed to rotate logs"
        EXIT_STATUS=1
    fi

    find "$LOG_DIR" -type f -name "*.log" | while read file; do
        date_str=$(date -r "$file" "+%Y-%m-%d")
        tar czf "/var/log/${date_str}_logs.tar.gz" "$file"
    done

    if [ -t 2 ]; then
        echo "About to remove old log files older than 7 days. Are you sure? (yes/no)"
        read -r -p "> " confirm
        if [ "${confirm,,}" = "yes" ]; then
            find "$LOG_DIR" -type f -name "*.log" -mtime +7 -delete
        else
            echo "Cleanup cancelled."
        fi
    else
        # If not running interactively, use non-interactive tools like find with rm to remove old logs
        if ! find "$LOG_DIR" -type f -name "*.log" -mtime +7 -exec rm {} \;; then
            echo "Failed to remove old log files"
            EXIT_STATUS=1
        fi
    fi

    end_time=$(date +%s)
    echo "Completed log cleanup at $(date)" | tee -a /var/log/cleanup.log
    echo "Cleanup time: $(bc <<< "scale=2; ($end_time - $start_time) / 60") minutes" | tee -a /var/log/cleanup.log

    # Rotate the log file to limit growth
    if ! logrotate -f /etc/logrotate.conf; then
        echo "Failed to rotate logs"
        EXIT_STATUS=1
    fi

    echo "Log files compressed and cleaned up." | tee -a /var/log/cleanup.log

    exit $EXIT_STATUS
done

# Ensure that the script cleans itself up if it encounters issues during execution
trap 'rm "/etc/logrotate.d/cleanup_log"' EXIT SIGTERM SIGHUP SIGINT

exit 0
