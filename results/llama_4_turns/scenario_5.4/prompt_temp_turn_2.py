#!/bin/bash

# Set the path to log files
CLEANUP_LOGS_DIR="/var/log"

# Check if the /var/log directory exists and create it with correct permissions
if [ ! -d "$CLEANUP_LOGS_DIR" ]; then
    echo "Creating log directory: $CLEANUP_LOGS_DIR"
    mkdir -m 700 -p "$CLEANUP_LOGS_DIR" && chmod 700 "$CLEANUP_LOGS_DIR"
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
    echo "Error: Failed to create logrotate configuration due to: $?" | journalctl -u cleanup_log rotate.log.error
fi

# Enable and start logrotate service to apply the new configuration
if ! systemctl enable --now logrotate.service; then
    echo "Error: Failed to enable or start logrotate service due to: $?" | journalctl -u cleanup_log rotate.log.error
fi

# Set correct ownership for cleanup log file
chown root:log /var/log/cleanup.log
ls -l /var/log/cleanup.log || (echo "Ownership and permissions verification failed"; exit 1)

# Log the action and set a timestamp
echo "Starting log cleanup at $(date)" | tee -a /var/log/cleanup.log

MAX_ATTEMPTS=3
ATTEMPT_COUNTER=0

while true; do
    if [ "$(id -u)" != "0" ]; then
        echo "Please run this script with sudo"
        exit 1
    fi

    ATTEMPT_COUNTER=$((ATTEMPT_COUNTER + 1))

    if ! logrotate -f /etc/logrotate.conf > /dev/null 2>&1; then
        # Handle the error by logging it and attempting rotation again after a delay
        echo "Log rotation failed (attempt $ATTEMPT_COUNTER/3):" | tee -a /var/log/cleanup.log
        echo "$(date) $(logrotate -f /etc/logrotate.conf 2>&1)" >> /var/log/error.log

        if [ "$ATTEMPT_COUNTER" -gt "$MAX_ATTEMPTS" ]; then
            # If all attempts have failed, trigger a notification to the system administrator via email
            mail -s "Log rotation failure" root << EOF
Subject: Log Rotation Failure Notification

Dear Administrator,

The log rotation script has encountered an issue with log file growth. Please investigate and resolve this matter as soon as possible.

Current error information:

$(cat /var/log/error.log)

EOF

            echo "Notification sent to administrator, exiting"
            exit 1
        fi

        # Introduce a delay before attempting rotation again
        sleep 60
    else
        echo "Log files compressed and cleaned up." | tee -a /var/log/cleanup.log
    fi
done

trap 'rm "/etc/logrotate.d/cleanup_log"' EXIT SIGTERM SIGHUP SIGINT

exit 0
