#!/bin/bash

# Define log directory
LOG_DIR="/var/logs"

# Function to safely remove files (to avoid accidental data loss)
safe_remove() {
    local file=$1
    echo "Attempting to delete $file..."
    if rm "$file"; then
        echo "Successfully deleted $file."
    else
        echo "Failed to delete $file. Insufficient permissions?" >&2
    fi
}

# Function to safely compress files
safe_compress() {
    local file=$1
    echo "Attempting to compress $file..."
    if tar -czvf "${file%.log}.tar.gz" -- "$file"; then
        echo "Successfully compressed $file."
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
find "$LOG_DIR" -type f -name "*.log" -mtime +7 -exec sh -c 'safe_remove "{}"' \;

# Check if the find command failed due to insufficient permissions
if [ $? -ne 0 ]; then
    echo "Error: Insufficient permissions to delete log files." >&2
    exit 1
fi

# Compress each remaining .log file
find "$LOG_DIR" -type f -name "*.log" -exec sh -c 'safe_compress "{}"' \;

