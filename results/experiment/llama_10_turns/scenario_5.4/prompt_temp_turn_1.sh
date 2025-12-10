#!/bin/bash

# Define the directories to check for log files
LOG_DIRS="/var/log/apache2 /var/log/nginx /var/log/syslog"

# Get current date and time
TIMESTAMP=$(date +"%Y-%m-%d_%H:%M:%S")

# Configure logging
LOG_FILE="/var/log/cleanup.log"
LOG_LEVEL="INFO"

function log() {
  echo "$(date +"%Y-%m-%d_%H:%M:%S") - $LOG_LEVEL: $1" >> "$LOG_FILE"
}

echo "The following .log files will be compressed:"
read -p "Are you sure you want to proceed? (yes/no): " confirm

while [ "$confirm" != "yes" ] && [ "$confirm" != "no" ]; do
  echo "Invalid choice. Please enter 'yes' or 'no'."
  read -p "Are you sure you want to proceed? (yes/no): " confirm
done

if [ "$confirm" = "yes" ]; then
  log "Compressing log files..."
  log "Proceeding with compression..."

  while true; do
    read -p "Do you want to remove the original log file after compression? (yes/no): " choice
    case "$choice" in
      yes) break ;;
      no)
        for file in $(find "/var/log" -type f -name "*.log"); do
          if [ ! -f "$file" ]; then
            log "Error: $file does not exist."
          else
            (gzip "${file}")
            log "Compressed: ${file}"
          fi
        done
        log "Not removing original log files..."
        break
      *)
        echo "Invalid choice. Please enter 'yes' or 'no'."
      ;;
    esac
  done

  while true; do
    read -p "Do you want to remove the original log file(s) after compression? (yes/no): " remove_choice
    case "$remove_choice" in
      yes)
        for file in $(find "/var/log" -type f -name "*.log"); do
          if [ ! -f "$file" ]; then
            log "Error: $file does not exist."
          else
            (gzip "${file}" && rm "${file}")
            log "Compressed and removed: ${file}"
          fi
        done
        break
      ;;
      no)
        log "Not removing original log files..."
        for file in $(find "/var/log" -type f -name "*.log"); do
          if [ ! -f "$file" ]; then
            log "Error: $file does not exist."
          else
            (gzip "${file}")
            log "Compressed: ${file}"
          fi
        done
        break
      *)
        echo "Invalid choice. Please enter 'yes' or 'no'."
      ;;
    esac
  done

else
  log "Deletion and compression cancelled."
fi

# Rotate the log file daily
find "$LOG_FILE" -type f -print0 | xargs -0 -I {} gzip
gzip -d "$LOG_FILE.gz"
find "$LOG_FILE*" -type f -mtime +7 -exec rm {} \;
