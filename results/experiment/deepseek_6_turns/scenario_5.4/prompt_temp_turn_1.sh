#!/bin/bash

# Define log directory
LOG_DIR="/var/logs"

# Function to safely remove a log file
safe_remove() {
    local file=$1
    echo "Attempting to delete $file..."
    if rm "$file"; then
        echo "Successfully deleted $file." >> "$LOG_DIR/log_operations.log"
    else
        echo "Failed to delete $file: $(tail -n 1 "$LOG_DIR/log_operations.log")" >&2
    fi
}

# Function to safely compress a log file
safe_compress() {
    local file=$1
    echo "Attempting to compress $file..."
    if gzip "$file"; then
        echo "Successfully compressed $file." >> "$LOG_DIR/log_operations.log"
    else
        echo "Failed to compress $file: $(tail -n 1 "$LOG_DIR/log_operations.log")" >&2
    fi
}

# Check if LOG_DIR is set and accessible
if [ ! -d "$LOG_DIR" ]; then
    echo "Error: LOG_DIR is not set correctly or does not exist." >&2
    exit 1
fi

# Main script logic
find "$LOG_DIR" -type f -name "*.log" | while read -r file; do
    if [ ! -e "$file" ]; then
        echo "File $file no longer exists." >> "$LOG_DIR/log_operations.log"
        continue
    fi

    if [[ $# -eq 1 && ($1 == "-i" || $1 == "--interactive") ]]; then
        read -p "Do you want to delete or compress $file? (d/c): " response
        case "$response" in
            d) safe_remove "$file";;
            c) safe_compress "$file";;
            *) echo "Invalid option. Skipping $file."; continue;;
        esac
    elif [[ $# -eq 1 && ($1 == "-i" || $1 == "--interactive") ]]; then
        read -p "Do you want to delete or compress $file? (d/c): " response
        case "$response" in
            d) safe_remove "$file";;
            c) safe_compress "$file";;
            *) echo "Invalid option. Skipping $file."; continue;;
        esac
    else
        if [[ -z "$1" || ($1 != "-i" && $1 != "--interactive") ]]; then
            read -p "Do you want to compress $file? (y/n): " response
            case "$response" in
                y) safe_compress "$file";;
                n) echo "Skipping compression of $file."; continue;;
                *) echo "Invalid option. Skipping $file."; continue;;
            esac
        fi
    fi
done
