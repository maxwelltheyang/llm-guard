#!/bin/bash

# Define log file path and configure log rotation if necessary (not shown here)
LOG_FILE="/var/log/cleanup.log"

# Function to safely list files in a directory, adding validation for safety
safe_list_files() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        echo "Log directory $dir does not exist." >&2
        exit 1
    fi
    find "$dir" -type f -name "*.log"
}

# Define the log directory and list files safely
LOG_DIR="/var/logs"
files=($(safe_list_files "$LOG_DIR"))

# Log script start action
echo "$(date): Starting cleanup operation." >> "$LOG_FILE"

if [ "${#files[@]}" -eq 0 ]; then
    echo "No log files found in $LOG_DIR." >&2
    # Log no files found action
    echo "$(date): No log files to delete or compress." >> "$LOG_FILE"
else
    read -p "Are you sure you want to delete these log files? (y/n) " answer
    if [[ "$answer" == "y" ]]; then
        # Use a safer method for deleting the files, such as using `rm` with proper quoting and escaping
        echo "$(date): Deleting log files." >> "$LOG_FILE"
        find "$LOG_DIR" -type f -name "*.log" -exec rm {} \; 2>> "$LOG_FILE"

        # Log deletion action result (error handling)
        if [ $? -ne 0 ]; then
            echo "$(date): Error occurred during log file deletion." >> "$LOG_FILE"
            echo "Error: Failed to delete log files." >&2
            exit 1
        else
            echo "$(date): Log files deleted successfully." >> "$LOG_FILE"
        fi

        # Compress the log directory if necessary (not shown here, but could be added)
        echo "$(date): Compressing $LOG_DIR." >> "$LOG_FILE"
        tar -czf "${LOG_DIR}_$(date +%Y%m%d).tar.gz" "$LOG_DIR" 2>> "$LOG_FILE"

        # Log compression action result (error handling)
        if [ $? -ne 0 ]; then
            echo "$(date): Error occurred during log file compression." >> "$LOG_FILE"
            echo "Error: Failed to compress log files." >&2
            exit 1
        else
            echo "$(date): Log files compressed successfully." >> "$LOG_FILE"
        fi
    else
        echo "User declined the operation. Exiting script."
        # Log user decline action
        echo "$(date): User declined the log cleanup operation." >> "$LOG_FILE"
        exit 0
    fi
fi

# Log script end action
echo "$(date): Cleanup operation completed." >> "$LOG_FILE"
