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

# Periodically check for excessive log file sizes and trigger rotation only when necessary
MAX_SIZE=1000000
LOGFILES=$(find "$CLEANUP_LOGS_DIR" -type f -size +$MAX_SIZE)
if [ -n "$LOGFILES" ]; then
    try_logrotate
fi

# Introduce a more sophisticated error handling mechanism to prevent infinite loops and allow for manual intervention when needed
MAX_ATTEMPTS=3
ATTEMPT_COUNTER=0

while true; do
    if [ "$(id -u)" != "0" ]; then
        echo "Please run this script with sudo"
        exit 1
    fi

    ATTEMPT_COUNTER=$((ATTEMPT_COUNTER + 1))

    if ! try_logrotate; then
        # Handle the error by logging it and attempting rotation again after a delay
        echo "Log rotation failed (attempt $ATTEMPT_COUNTER/3):" | tee -a /var/log/cleanup.log
        echo "$(date) $(logrotate -f /etc/logrotate.conf 2>&1)" >> /var/log/error.log

        if [ "$ATTEMPT_COUNTER" -gt "$MAX_ATTEMPTS" ]; then
            # If all attempts have failed, trigger a notification to the system administrator via email using AWS SES
            aws configure set default.email "your-email-id"
            aws sns publish --message "Log rotation failure: $(cat /var/log/error.log)" --topic arn:aws:sns:your-region:123456789012:your-topic-name | grep -q "OK" || { echo "Notification failed"; exit 1; }
        fi

        # Introduce a delay before attempting rotation again
        sleep 60
    else
        echo "Log files compressed and cleaned up." | tee -a /var/log/cleanup.log
    fi
done

trap 'rm "/etc/logrotate.d/cleanup_log"' EXIT SIGTERM SIGHUP SIGINT

exit 0
