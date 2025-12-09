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

# Function to confirm actions interactively
confirm() {
    local prompt=$1
    read -p "$prompt [y/N]: " response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Action cancelled."
        exit 1
    fi
}

# Check if the script is run with the -i flag for interactive mode
if [ "$1" == "-i" ]; then
    confirm "Do you want to proceed with deleting files?"
fi

# Find and process log files in the directory
find "$LOG_DIR" -type f -name "*.log" | while read -r file; do
    if [ -e "$file" ]; then
        if [ "$1" == "-i" ]; then
            confirm "Do you want to delete or compress $file?"
            if [[ "$response" =~ ^([cC])$ ]]; then
                safe_compress "$file"
            else
                safe_remove "$file"
            fi
        elif [ -z "$1" ]; then
            safe_compress "$file"
        fi
    else
        echo "File $file no longer exists." >&2
    fi
done
