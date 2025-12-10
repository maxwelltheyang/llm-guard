#!/bin/bash

# Define the directories to check for log files
LOG_DIRS="/var/log/apache2 /var/log/nginx /var/log/syslog"

# Get current date and time
TIMESTAMP=$(date +"%Y-%m-%d_%H:%M:%S")

echo "The following .log files will be compressed:"
read -p "Are you sure you want to proceed? (yes/no): " confirm

while [ "$confirm" != "yes" ] && [ "$confirm" != "no" ]; do
  echo "Invalid choice. Please enter 'yes' or 'no'."
  read -p "Are you sure you want to proceed? (yes/no): " confirm
done

if [ "$confirm" = "yes" ]; then
  log_files=$(find "/var/log" -type f -name "*.log")
  echo "Compressing log files..."

  while true; do
    read -p "Do you want to remove the original log file after compression? (yes/no): " choice
    case "$choice" in
      yes) break ;;
      no)
        for file in $log_files; do
          if [ ! -f "$file" ]; then
            echo "Error: $file does not exist."
          else
            (gzip "${file}")
            echo "Compressed: ${file}"
          fi
        done
        exit 0 ;;
      *) echo "Invalid choice. Please enter 'yes' or 'no'." ;;
    esac
  done

  while true; do
    read -p "Do you want to remove the original log file(s) after compression? (yes/no): " remove_choice
    case "$remove_choice" in
      yes)
        for file in $log_files; do
          if [ ! -f "$file" ]; then
            echo "Error: $file does not exist."
          else
            (gzip "${file}" && rm "${file}")
            echo "Compressed and removed: ${file}"
          fi
        done
        break
      ;;
      no)
        for file in $log_files; do
          if [ ! -f "$file" ]; then
            echo "Error: $file does not exist."
          else
            (gzip "${file}")
            echo "Compressed: ${file}"
          fi
        done
        break
      ;;
      *)
        echo "Invalid choice. Please enter 'yes' or 'no'."
      ;;
    esac
  done
else
  echo "Deletion and compression cancelled."
fi
