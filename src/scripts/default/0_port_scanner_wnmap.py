import nmap
import sys
from utils.print import print_success, print_error, print_process_step

def run(host, project_name):
    try:
        nm = nmap.PortScanner()
        print_process_step(f"Starting Nmap scan on host {host}")
        nm.scan(host, arguments=f"-sC -sV")

        print_process_step(f"Executing: [{nm.command_line()}]")
        print_process_step(f"Saving Scan Results to: {project_name}.csv")
        with open(f'{project_name}.csv', 'w') as writer:
            writer.write(nm.csv())
        return {'scan_result' : f"{project_name}.csv"}
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)