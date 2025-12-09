#!/bin/bash

# Define log directory
LOG_DIR="/var/logs"
LOG_FILE="$LOG_DIR/log_operations.log"

# Function to safely remove a log file
safe_remove() {
    local file=$1
    echo "Attempting to delete $file..." >> "$LOG_FILE"
    if rm "$file"; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted: $file" >> "$LOG_FILE"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Failed to delete: $file" >> "$LOG_FILE"
    fi
}

# Function to safely compress a log file
safe_compress() {
    local file=$1
    echo "Attempting to compress $file..." >> "$LOG_FILE"
    if gzip "$file"; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Compressed: $file" >> "$LOG_FILE"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Failed to compress: $file" >> "$LOG_FILE"
    fi
}

# Check if LOG_DIR exists and is writable
if [ ! -w "$LOG_DIR" ]; then
    echo "Error: Log directory '$LOG_DIR' does not exist or is not writable." >&2
    exit 1
fi

# Main script logic starts here
echo "$(date '+%Y-%m-%d %H:%M:%S') - Script started." >> "$LOG_FILE"

if [ $# -eq 0 ]; then
    echo "Usage: $0 [-i|--interactive]" >&2
    exit 1
fi

INTERACTIVE=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        -i|--interactive)
            INTERACTIVE=true
            shift
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

if $INTERACTIVE; then
    while true; do
        read -p "Do you want to delete or compress the log file? (d/c): " response
        case "$response" in
            d) safe_remove "$LOG_FILE"; break ;;
            c) safe_compress "$LOG_FILE"; break ;;
            *) echo "Invalid input. Please enter 'd' for delete or 'c' for compress." ;;
        esac
    done
else
    # If not in interactive mode, simply attempt to compress the log file
    if [ -f "$LOG_FILE" ]; then
        safe_compress "$LOG_FILE"
    else
        echo "Log file does not exist: $LOG_FILE" >&2
        exit 1
    fi
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - Script finished." >> "$LOG_FILE"
