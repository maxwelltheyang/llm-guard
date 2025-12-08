#!/bin/bash

# Define log directory
LOG_DIR="/var/logs"

# Find and delete old log files older than 7 days
find "$LOG_DIR" -type f -name "*.log" -mtime +7 -exec rm {} \;

# Compress current log files
tar czvf logs_$(date +"%Y%m%d").tar.gz "$LOG_DIR"/log*
