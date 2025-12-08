import argparse
import os
import subprocess
import sys
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Walk a results directory and run pipreqs in each "
            "scenario_*/prompt_* folder to generate requirements.txt."
        )
    )
    parser.add_argument(
        "root",
        help="Root directory that contains scenario_* folders (e.g. results\\20251207_015129)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing requirements.txt files (passes --force to pipreqs).",
    )

    args = parser.parse_args()

    # Ensure pipreqs exists
    if shutil.which("pipreqs") is None:
        print(
            "Error: pipreqs not found on PATH. Install it with `pip install pipreqs`.",
            file=sys.stderr,
        )
        sys.exit(1)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory.", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning under root: {root}")

    # Walk all directories
    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)
        dir_name = current_dir.name
        parent_name = current_dir.parent.name

        # We only care about prompt_* directories whose parent is scenario_*
        if not dir_name.startswith("prompt_"):
            continue
        if not parent_name.startswith("scenario_"):
            continue

        # Only bother if there is at least one .py file
        has_py = any(name.endswith(".py") for name in filenames)
        if not has_py:
            print(f"Skipping {current_dir} (no .py files found).")
            continue

        cmd = ["pipreqs", str(current_dir)]
        if args.force:
            cmd.append("--force")

        print(f"\n=== Running pipreqs in {current_dir} ===")
        print("Command:", " ".join(cmd))

        result = subprocess.run(cmd, text=True)
        if result.returncode == 0:
            print(f"Successfully generated requirements.txt in {current_dir}")
        else:
            print(
                f"pipreqs failed in {current_dir} with exit code {result.returncode}",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
