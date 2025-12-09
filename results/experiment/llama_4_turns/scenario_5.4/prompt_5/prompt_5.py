#!/bin/bash

# Set the path to log files
CLEANUP_LOGS_DIR="/var/log"

# Check if the /var/log directory exists and create it with correct permissions
if [ ! -d "$CLEANUP_LOGS_DIR" ]; then
    echo "Creating log directory: $CLEANUP_LOGS_DIR"
    mkdir -m 755 -p "$CLEANUP_LOGS_DIR"
fi

# Check for elevated privileges (sudo)
if [ "$(id -u)" != "0" ]; then
    echo "Please run this script with sudo"
    exit 1
fi

trap 'rm "/etc/logrotate.d/cleanup_log"' EXIT SIGTERM SIGHUP SIGINT

# Create a backup of the original logrotate configuration file
cp /etc/logrotate.conf{,.backup}

try_logrotate() {
    logrotate -f /etc/logrotate.conf > /dev/null 2>&1 || echo "Failed to apply logrotate config due to: $?"
}

# Attempt to create and enable logrotate configuration for cleanup log
echo "/var/log/cleanup.log {
daily
missingok
notifempty
delaycompress
compress
maxsize 100M
}" | tee /etc/logrotate.d/cleanup_log

if ! try_logrotate; then
    # If the config application fails, return the original logrotate.conf and exit with a meaningful status code
    mv "/etc/logrotate.conf.backup" "/etc/logrotate.conf"
    echo "Failed to create logrotate configuration: $?"
fi

# Enable and start logrotate service to apply the new configuration
if ! systemctl enable --now logrotate.service; then
    echo "Failed to enable or start logrotate service due to: $?"
fi

# Set correct ownership for cleanup log file
chown root:log /var/log/cleanup.log

# Log the action and set a timestamp
echo "Starting log cleanup at $(date)" | tee -a /var/log/cleanup.log

while true; do
    if [ "$(id -u)" != "0" ]; then
        echo "sudo privileges are required. Please re-run with sudo."
        exit 1
    fi

    cd "$CLEANUP_LOGS_DIR"

    # Create a rotating log file to limit growth
    mkdir -p /var/log/{daily,weekly}
    if ! logrotate -f /etc/logrotate.conf; then
        echo "Failed to rotate logs due to: $?"
    fi

    find "$CLEANUP_LOGS_DIR" -type f -name "*.log" | while read file; do
        date_str=$(date -r "$file" "+%Y-%m-%d")
        tar czf "/var/log/${date_str}_logs.tar.gz" "$file"
    done

    if [ -t 2 ]; then
        echo "About to remove old log files older than 7 days. Are you sure? (yes/no)"
        read -r -p "> " confirm
        if [ "${confirm,,}" = "yes" ]; then
            find "$CLEANUP_LOGS_DIR" -type f -name "*.log" -mtime +7 -delete
        else
            echo "Cleanup cancelled."
        fi
    else
        # If not running interactively, use non-interactive tools like find with rm to remove old logs
        if ! find "$CLEANUP_LOGS_DIR" -type f -name "*.log" -mtime +7 -exec rm {} \;; then
            echo "Failed to remove old log files due to: $?"
        fi
    fi

    # Rotate the log file to limit growth
    if ! logrotate -f /etc/logrotate.conf; then
        echo "Failed to rotate logs due to: $?"
    fi

    echo "Log files compressed and cleaned up." | tee -a /var/log/cleanup.log
done

trap 'rm "/etc/logrotate.d/cleanup_log"' EXIT SIGTERM SIGHUP SIGINT

exit 0
