#!/bin/bash

# Define log file path and configure rotation if necessary (not shown here)
LOG_FILE="/var/log/cleanup.log"

# Function to safely list files in a directory
safe_list_files() {
    local dir="$1"
    # Validate the directory before listing files
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
        echo "$(date): Deleting log files from $LOG_DIR." >> "$LOG_FILE"
        rm "${files[@]}" 2>> "$LOG_FILE"

        # Log the result of the deletion action
        if [ $? -ne 0 ]; then
            echo "Error: Failed to delete log files." >&2
            echo "$(date): Error: Failed to delete log files." >> "$LOG_FILE"
            exit 1
        else
            echo "$(date): Log files deleted successfully from $LOG_DIR." >> "$LOG_FILE"
        fi
    fi

    # Compress the LOG_DIR if necessary (not shown here, but could be added)
    echo "$(date): Compressing $LOG_DIR." >> "$LOG_FILE"
    tar -czf "${LOG_DIR}_$(date +%Y%m%d).tar.gz" "${LOG_DIR}" 2>> "$LOG_FILE"

    # Log the result of the compression action
    if [ $? -ne 0 ]; then
        echo "Error: Failed to compress log files." >&2
        echo "$(date): Error: Failed to compress log files." >> "$LOG_FILE"
        exit 1
    else
        echo "$(date): Log files compressed successfully from $LOG_DIR." >> "$LOG_FILE"
    fi

    # Log the end of the operation
    echo "$(date): Log cleanup operation completed successfully." >> "$LOG_FILE"
} |& tee -a "$LOG_FILE"  # Append output to log file and display in terminal
