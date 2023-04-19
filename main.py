import argparse
import subprocess
import os

project_name  = input("Enter Project Name:")
ip = input("Enter IP Address of the WebApp:")

def run_command(cmd):
    cmd_split = cmd.split()
    print(f"Running command: {cmd}")
    p = subprocess.run(cmd_split, capture_output=True, text=True)
    print(f"Status Code: {p.returncode}")
    if p.returncode:
        raise subprocess.CalledProcessError(p.returncode, cmd.split())
    print(subprocess.check_output(cmd_split, text=True))


def main():
    # import scripts.directory_busting as sdb
    # sdb.directory_busting('http://127.0.0.1:8000', './test_wordlist.txt')
    import scripts.port_scanner_wnmap as wnmap
    wnmap.create_ps("127.0.0.1", "abcd")

if __name__ == "__main__":
    main()