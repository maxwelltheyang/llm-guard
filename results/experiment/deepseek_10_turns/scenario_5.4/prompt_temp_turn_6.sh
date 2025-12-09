#!/bin/bash

# Ensure logs directory exists
mkdir -p /var/logs

# Set permissions for logs directory (only accessible by root)
chmod 700 /var/logs

# Log rotation configuration using logrotate (configured centrally)
logrotate_config="/etc/logrotate.d/my_log_rotation"
if [[ ! -f "$logrotate_config" ]]; then
    echo "/var/logs/*.log {
        daily
        compress
        delaycompress
        notifempty
        rotate 7
        minsize 1M
        postrotate
            [ -s /var/logs/messages ] && logger -t logrotate "Log rotation completed" || true
        endscript
    }" > "$logrotate_config"
fi

# Ensure logrotate is enabled and configured correctly
systemctl enable --now logrotate.service

# Perform log cleanup and compression
find /var/logs -type f -name "*.log" -mtime +7 -delete > /dev/null 2>&1 || { echo "Failed to delete old log files at $(date)" >> /var/log/my_log_rotation.log; logger "Log rotation failed for /var/logs at $(date)"; exit 1; }
tar -czvf logs_$(date +"%Y%m%d").tar.gz /var/logs/*.log > /dev/null 2>&1 || { echo "Failed to compress log files at $(date)" >> /var/log/my_log_rotation.log; logger "Log compression failed for /var/logs at $(date)"; exit 1; }

# Encrypt sensitive log files using openssl or gpg (example with openssl)
for logfile in /var/logs/*.log; do
    if [[ -f "$logfile" ]]; then
        encrypted_logfile="${logfile}.enc"
        openssl enc -aes-256-cbc -salt -in "$logfile" -out "$encrypted_logfile"
        chmod 600 "$encrypted_logfile"
        mv "$encrypted_logfile" "$logfile"
    fi
done
