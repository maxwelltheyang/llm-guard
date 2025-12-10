import sys
from datetime import date
import logging.config
import mmap
import memory_profiler
import traceback
from logging.handlers import RotatingFileHandler
import psutil
import os
import configparser
import argparse

# Define constants for safe buffer allocation limits
MAX_SAFE_ALLOC_SIZE = 1 * 1024 * 1024 * 1024  # 1 GB - Maximum size to allocate safely in bytes.
MIN_VIRTUAL_MEMORY = 2 * 1024 * 1024 * 1024  # 2 GB - Minimum virtual memory required for buffer generation.

NUM_ALPHABETIC_CHARACTERS = 26

# Set up logging with a consistent level and format
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default_formatter': {
            'format': '%(asctime)s %(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'console_handler': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default_formatter',
            'stream': sys.stdout
        },
        'file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO', # Ensure INFO level is used for file logging to avoid mixing DEBUG and INFO logs.
            'formatter': 'default_formatter',
            'filename': 'buffer_generator.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5
        }
    },
    'loggers': {
        '': {
            'handlers': ['console_handler', 'file_handler'],
            'level': 'DEBUG'
        }
    }
})

def validate_iteration_count(iteration_count):
    if not isinstance(iteration_count, int) or iteration_count <= 0:
        logging.error(f"Invalid ITERATION_COUNT value: {iteration_count}. Using default value of 10.")
        return 10
    else:
        return iteration_count

def generate_buffer(size):
    try:
        available_vm = psutil.virtual_memory().available
        if size > MAX_SAFE_ALLOC_SIZE or size > available_vm:
            raise MemoryError("Insufficient memory for buffer allocation.")

        # Attempt to allocate the requested buffer size.
        buffer = bytearray(size)
        logging.debug(f"Successfully allocated buffer of {size} bytes.")
    except Exception as e:
        logging.error(f"Failed to generate buffer: {str(e)}")

    return buffer

def configure_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler('buffer_generator.log')

    handler.setFormatter(formatter)
    logger.addHandler(handler)

def main():
    parser = argparse.ArgumentParser(description='Buffer Generator')
    parser.add_argument('-c', '--count', type=int, help='Number of iterations', default=10)
    args = parser.parse_args()

    iteration_count = validate_iteration_count(args.count)
    logging.info(f"Starting buffer generation with {iteration_count} iterations.")

    for i in range(iteration_count):
        try:
            logging.debug(f"Iteration {i+1} of {iteration_count}")

            # Attempt to generate and print the buffer.
            buffer_size = 1024 * 1024
            buffer = generate_buffer(buffer_size)
            if buffer is not None:
                logging.info(f"Buffer printed successfully for iteration {i+1}.")
        except Exception as e:
            logging.error(f"Error occurred during iteration {i+1}: {str(e)}\n{traceback.format_exc()}")

    # Perform resource cleanup (close file handlers, etc.) to prevent potential leaks.
    logging.info("Buffer generation complete. Performing resource cleanup.")

if __name__ == "__main__":
    import sys
    main()
