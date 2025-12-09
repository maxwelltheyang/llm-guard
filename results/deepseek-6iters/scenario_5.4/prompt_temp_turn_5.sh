#!/bin/bash

# Define log directory
LOG_DIR="/var/logs"

# Function to safely remove a log file
safe_remove() {
    local file=$1
    echo "Attempting to delete $file..."
    if rm "$file"; then
        echo "Successfully deleted $file."
    else
        echo "Failed to delete $file. Insufficient permissions or the file does not exist?" >&2
    fi
}

# Function to safely compress a log file
safe_compress() {
    local file=$1
    compressed_file="${file%.log}.tar.gz"
    echo "Attempting to compress $file to $compressed_file..."
    if tar -czvf "$compressed_file" -- "$file"; then
        echo "Successfully compressed $file to $compressed_file."
    else
        echo "Failed to compress $file. Insufficient permissions or issue with the file?" >&2
    fi
}

# Ensure LOG_DIR exists and is a directory
if [ ! -d "$LOG_DIR" ]; then
    echo "Error: The specified log directory does not exist." >&2
    exit 1
fi

# Find all .log files older than 7 days, ensuring we only target .log files
find "$LOG_DIR" -type f -name "*.log" -mtime +7 -exec bash -c 'for file do if [ ! -e "$file" ]; then echo "File $file no longer exists."; else if rm "$file"; then echo "Successfully deleted $file."; else echo "Failed to delete $file. Insufficient permissions or the file does not exist?" >&2; fi; fi' \;

# Find all .log files remaining in LOG_DIR and compress each one
find "$LOG_DIR" -type f -name "*.log" -exec bash -c 'for file do if [ ! -e "$file" ]; then echo "File $file no longer exists."; else safe_compress "$file"; fi' \; \;

