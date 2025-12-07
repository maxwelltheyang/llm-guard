#!/bin/bash

# Set the path to log files
CLEANUP_LOGS_DIR="/var/log"

# Create a backup of the original logrotate configuration file
cp /etc/logrotate.conf{,.backup}

try_logrotate() {
    logrotate -f /etc/logrotate.conf > /dev/null 2>&1 || echo "Failed to apply logrotate config due to: $?"
}

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
        # Log critical errors in a separate file /var/log/error.log
        if [ ! -d "/var/log" ]; then mkdir -p "/var/log"; fi
        touch /var/log/error.log || { echo "Error creating log file: $?" >&2; exit 1; }

        echo "$(date +"%Y-%m-%d %H:%M:%S"): Log rotation failed. Error: $(cat /var/log/error.log)" | tee -a "/var/log/error.log" >&2

        if [ "$ATTEMPT_COUNTER" -gt "$MAX_ATTEMPTS" ]; then
            # If all attempts have failed, trigger a notification to the system administrator via email using AWS SES
            aws configure set default.email "your-email-id"
            response=$(aws sns publish --message "Log rotation failure: $(cat /var/log/error.log)" --topic arn:aws:sns:your-region:123456789012:your-topic-name)
            if [ $? -eq 0 ]; then
                echo "$(date +"%Y-%m-%d %H:%M:%S"): Notification sent successfully." | tee -a "/var/log/notification.log"
            else
                # If SES notification fails, trigger an email notification (e.g., using `sendmail`)
                sendmail -t <<EOF
To: your-email-id
Subject: Log rotation failure

Dear Administrator,

Log rotation has failed. Please check /var/log/error.log for details.

Sincerely,
$(hostname)
EOF
            fi
        else
            # Introduce a delay before attempting rotation again
            sleep 60
        fi
    else
        echo "Log files compressed and cleaned up." | tee -a "/var/log/cleanup.log"
    fi
done

exit 0
