#!/bin/bash

# Delete .log files older than 7 days
find /var/logs/ -name "*.log" -type f -mtime +7 -exec rm -f {} \;

# Compress current .log files
find /var/logs/ -name "*.log" -type f -mtime -7 -exec gzip {} \;
