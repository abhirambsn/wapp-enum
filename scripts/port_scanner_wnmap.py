import nmap
import sys

def create_ps(host, project_name):
    try:
        nm = nmap.PortScanner()
        nm.scan(host, arguments=f"-sC -sV -sS -oA {project_name}", sudo=True)
        print(f"Executing: [{nm.command_line()}]")
    except Exception as e:
        print(f"Error {e}")
        sys.exit(1)