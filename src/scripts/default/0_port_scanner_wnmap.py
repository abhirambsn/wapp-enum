import nmap
import sys
import csv

def run(host, project_name):
    try:
        nm = nmap.PortScanner()
        print(f"[*] Starting Nmap scan on host {host}")
        nm.scan(host, arguments=f"-sC -sV")

        print(f"[*] Executing: [{nm.command_line()}]")
        print(f"[+] Saving Scan Results to: {project_name}.csv")
        with open(f'{project_name}.csv', 'w') as writer:
            writer.write(nm.csv())
        return {'scan_result' : f"{project_name}.csv"}
    except Exception as e:
        print(f"[x] Error: {e}")
        sys.exit(1)