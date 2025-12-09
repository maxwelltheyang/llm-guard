#!/bin/bash

# Define constants with default values from environment variables if available
readonly LOG_DIR="${ENV_VAR_LOG_DIR:-/var/log}"
readonly LOG_FILE="${ENV_VAR_LOG_FILE:-/var/log/cleanup.log}"

# Function to check if a variable is set and not empty
check_variable() {
    local varname=$1
    eval "local value=\$${varname}"
    if [ -z "${value}" ]; then
        echo "Error: ${varname} is not set." >&2
        exit 1
    fi
}

# Check that LOG_DIR and LOG_FILE are properly set
check_variable LOG_DIR
check_variable LOG_FILE

# Script logic...
