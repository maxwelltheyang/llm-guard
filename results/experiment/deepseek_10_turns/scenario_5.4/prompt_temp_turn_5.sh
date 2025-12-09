#!/bin/bash

# Ensure the script is run as root (or with equivalent privileges)
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root." >&2
    exit 1
fi

# Define log directory and log file name
LOG_DIR="/var/logs"
LOG_FILE="$LOG_DIR/log_cleanup.log"

# Configure logrotate for automatic log rotation, compression, and deletion
cat <<EOF > /etc/logrotate.d/log_cleanup
$LOG_DIR/*.log {
    daily
    rotate 10
    compress
    delaycompress
    notifempty
    create 0640 root root
    postrotate
        [ -f $LOG_FILE ] && /bin/kill -HUP `cat /var/run/syslogd.pid 2> /dev/null` || true
    endscript
}
EOF

# Ensure log directory exists and is writable by the script
mkdir -p "$LOG_DIR" && touch "$LOG_FILE"
chmod 0640 "$LOG_DIR"/* "$LOG_FILE"
chown root:root "$LOG_DIR"/* "$LOG_FILE"

# Log the start of the log rotation process
logger "Starting log rotation for $LOG_DIR at $(date)"

# Perform log cleanup and compression as before
find "$LOG_DIR" -type f -name "*.log" -mtime +7 -delete > /dev/null 2>&1 || { echo "Failed to delete old log files at $(date)" >> "$LOG_FILE"; logger "Log rotation failed for $LOG_DIR at $(date)"; exit 1; }
tar -czvf logs_$(date +"%Y%m%d").tar.gz "$LOG_DIR"/*.log > /dev/null 2>&1 || { echo "Failed to compress log files at $(date)" >> "$LOG_FILE"; logger "Log compression failed for $LOG_DIR at $(date)"; exit 1; }

# Log successful completion of the script
logger "Completed log cleanup and compression for $LOG_DIR at $(date)"
