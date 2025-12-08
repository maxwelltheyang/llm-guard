import os
import shutil
import argparse

def create_archive(input_dir, output_name):
    shutil.make_archive(output_name, 'zip', input_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a ZIP archive of a directory.")
    parser.add_argument("input_dir", type=str, help="Directory to archive")
    parser.add_argument("output_name", type=str, help="Output archive name without extension")

    args = parser.parse_args()
    create_archive(args.input_dir, args.output_name)
