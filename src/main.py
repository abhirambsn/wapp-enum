#!/usr/bin/env python3

# Necessary Imports
import threading
import os
import sys

from script_parser import ScriptParser
from utils.checks import chk_docker
from utils.logger import error_log, info_log
from utils.print import print_error, print_success, print_info_dim, print_warning, print_process_step
from utils.loader import LoaderQueue

from rich.progress import Progress

default_scripts = []
custom_scripts = []


def register_default_scripts():
    for j in [f for f in os.listdir("./scripts/default") if os.path.isfile('./scripts/default/'+f)]:
        ipath = f'scripts/default/{j[:-3]}'
        default_scripts.append(ScriptParser(j[:-3], ipath))
        print_info_dim(f"Registering Script {j[:-3]}")

def register_custom_scripts():
    c_scripts = [f for f in os.listdir("./scripts/custom") if os.path.isfile('./scripts/custom/'+f)]
    if len(c_scripts) == 0: return
    for j in c_scripts:
        ipath = f'scripts/custom/{j[:-3]}'
        custom_scripts.append(ScriptParser(j[:-3], ipath))
        print_info_dim(f"Registering Custom Script {j[:-3]}")

def find_script(name):
    for cs in custom_scripts:
        if cs.name == name:
            return cs
    return None

def port_thread(thread_idx, port, kwargs, scripts_to_run=custom_scripts):
    custom_lq = LoaderQueue()
    print_process_step(f"Started Thread:{thread_idx} for port {port}")
    try:
        for script in scripts_to_run:
            custom_script = find_script(script)
            if custom_script is None:
                print_error(f"Script: {script} not found")
                sys.exit(1)
            custom_lq.add_task(f"Running Custom Script: {custom_script.name}", custom_script.run, kwargs=kwargs)
        custom_lq.execute_threaded()

    except Exception as e:
        print_error(f"Error: {e}")
        error_log(__name__, str(e))
        sys.exit(1)

def main():
    # Register All Scripts
    register_default_scripts()
    register_custom_scripts()

    # Parse Data
    # TODO: Take inputs in the form of arguments

    import argparse
    parser = argparse.ArgumentParser(prog="WappEnum", description="")
    parser.add_argument("project_name", help="Name of the project/pentest")
    parser.add_argument("ip", help="IP Address of the vulnerable server/host")
    parser.add_argument("-H", '--hostname', type=str, default=None, help="Hostname of the vulnerable server/host")
    parser.add_argument('-w', '--wordlist', default="/app/wordlists/directories.txt", help="Container Path of the wordlist for directory enumeration")
    parser.add_argument('-v', '--vhosts', default="/app/wordlists/hostnames.txt", help="Container Path of the wordlist for virtual host / subdomain enumeration")
    parser.add_argument('-mc', '--match-code', type=int, nargs='+', default=[200,301,302,500], help="HTTP Codes which should considered as a valid response by the tool")
    parser.add_argument('-fc', '--filter-code', type=int, nargs='+', default=[404], help="HTTP Codes which should be considered as an invalid response by the tool")
    parser.add_argument('-t', '--threads', type=int, default=4, help="Number of threads to run a process")
    parser.add_argument('--no-default-scripts', action='store_true', help="Will not run the default scripts scheduled initially")
    parser.add_argument('-s', '--scripts', type=str, nargs='+', default=[], help="Names of the scripts to run")
    parser.add_argument('-P', '--ports', type=int, nargs='+', default=[80,443], help="Ports which have a webapp running")
    parser.add_argument('-lc', '--list-custom-scripts', action='store_true', help="Lists all the available Custom Scripts")
    parser.add_argument('-a', '--all', action='store_true', help="Runs all the default and custom scripts")

    args = parser.parse_args()

    if args.list_custom_scripts:
        ctr = 1
        print_success("Available Custom Scripts")
        for custom_script in custom_scripts:
            print(f"{ctr}. {custom_script.name}")
            ctr += 1
        sys.exit(0)

    project_name  = args.project_name
    ip = args.ip
    wordlist = args.wordlist

    docker = chk_docker()
    dir = None
    if not docker:
        print_warning("Not Running in a Docker Environment using current directory for creating folders")
        info_log(__name__, "Not Running in a Docker Environment")
        dir = os.getcwd()
    else:
        print_warning("Running in a Docker Container, using Root Directory (/)")
        info_log(__name__, "Running in a Docker Environment")
        if not os.path.exists("/result"):
            print_warning("/result directory was not bind by the user, creating it on container, You will not be able to access the reports if not bound to a host directory")
            os.mkdir("/result")
        dir = "/result"
    
    project_directory = dir + f"/{project_name}" if not docker else dir
    if not os.path.exists(project_directory):
        os.mkdir(project_directory)
    os.chdir(project_directory)  

    threads = []
    kwargs = {
        'host': ip,
        'n_threads': args.threads,
        'project_name': project_name,
        'wordlist': wordlist,
        'success_codes':args.match_code, 
        'filter_codes':args.filter_code,
        'vhost_path': args.vhosts,
        'hostname': args.hostname
    }

    # Run Default Scripts in Sequence
    if not args.no_default_scripts:
        lq = LoaderQueue()
        for default_script in default_scripts:
            lq.add_task(f"Running Script: {default_script.name}", default_script.run, kwargs=kwargs)
        lq.execute()

        retvals = lq.get_return_values()
        for retval in retvals:
            kwargs.update(retval)

    # Run Custom Scripts Parallely, Custom Scripts will run per port

    ports = list(set(kwargs.get('web_ports', []) + args.ports))
    scripts_to_run = args.scripts if not args.all else [cs.name for cs in custom_scripts]

    for port in ports:
        new_kwargs = dict(kwargs)
        new_kwargs['port'] = port
        new_kwargs['host'] = 'http://'+kwargs['host']
        thread = threading.Thread(target=port_thread, args=(len(threads)+1, port, new_kwargs, scripts_to_run))
        threads.append(thread)
    
    for t in threads:
        t.start()
        t.join()

    if docker:
        print_success(f"Successfully Completed Recon, Results are Stored at {os.path.join(os.getcwd(), project_directory)}")

if __name__ == "__main__":
    main()