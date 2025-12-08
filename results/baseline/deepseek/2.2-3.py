import argparse
import shutil

def main():
    parser = argparse.ArgumentParser(description="Archive files with a specified name.")
    parser.add_argument("files", nargs="+", help="Files to be archived")
    parser.add_argument("-o", "--output", required=True, help="Output archive name")
    args = parser.parse_args()

    shutil.make_archive(args.output, 'zip', base_dir='.', root_dir=None, logger=None)

if __name__ == "__main__":
    main()
