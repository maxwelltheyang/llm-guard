#!/bin/bash

# Define log directory
LOG_DIR="/var/logs"

# Find all .log files older than 7 days and delete them
find "$LOG_DIR" -type f -name "*.log" -mtime +7 -exec rm {} \;

# Compress the remaining .log files
tar -czvf logs_$(date +"%Y%m%d").tar.gz $LOG_DIR/*.log
