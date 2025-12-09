#!/bin/bash

# Define constants with default values
readonly LOG_DIR="/var/log"
readonly LOG_FILE="/var/log/cleanup.log"

# Function to safely list files in a directory
safe_list_files() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        find "$dir" -type f -name "*.log"
    else
        echo "Directory $dir does not exist." >&2
        return 1
    fi
}

# Main script logic
{
    # Log the start of the operation
    echo "$(date): Starting log cleanup operation." >> "$LOG_FILE"

    # List and potentially delete files in the LOG_DIR
    if ! files=($(safe_list_files "$LOG_DIR")); then
        echo "Error: Failed to list or validate log files in $LOG_DIR." >&2
        echo "$(date): Error: Failed to list or validate log files in $LOG_DIR." >> "$LOG_FILE"
        exit 1
    fi

    # Log the action of deleting files
    if [[ ${#files[@]} -eq 0 ]]; then
        echo "No log files found to delete in $LOG_DIR." >> "$LOG_FILE"
    else
        echo "$(date): Deleting log files..." >> "$LOG_FILE"
        rm "${files[@]}" 2>&1 | tee -a "$LOG_FILE"
        if [[ $? -ne 0 ]]; then
            echo "Error: Failed to delete log files." >> "$LOG_FILE"
            exit 1
        fi
    fi

    # Log the action of compressing the log directory
    echo "$(date): Compressing log directory..." >> "$LOG_FILE"
    tar -czf "${LOG_DIR}_$(date +%Y%m%d).tar.gz" "${LOG_DIR}" 2>&1 | tee -a "$LOG_FILE"
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to compress log directory." >> "$LOG_FILE"
        exit 1
    fi

    # Log the completion of the operation
    echo "$(date): Log cleanup operation completed successfully." >> "$LOG_FILE"
}
