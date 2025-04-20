#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys

def main():
    target = "./inputs"

    if not os.path.isdir(target):
        print(f"Error: '{target}' is not a directory", file=sys.stderr)
        sys.exit(1)

    for entry in os.listdir(target):
        path = os.path.join(target, entry)
        if not os.path.isfile(path):
            continue

        cmd_to_run = f"mcnp6 i={target}/{entry} o=./outputs/o-{entry.split('.')[0]}.o tasks 26"

        try:
            subprocess.run(cmd_to_run, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed on '{path}' with exit code {e.returncode}", file=sys.stderr)

if __name__ == "__main__":
    main()
