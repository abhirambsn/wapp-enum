# Necessary Imports
import threading
import os
import sys

from script_parser import ScriptParser

default_scripts = []
custom_scripts = []

def register_default_scripts():
    for j in [f for f in os.listdir("./scripts/default") if os.path.isfile('./scripts/default/'+f)]:
        ipath = f'scripts/default/{j[:-3]}'
        default_scripts.append(ScriptParser(j[:-3], ipath))
        print(f"[+] Registering Script {j[:-3]}")

def register_custom_scripts():
    c_scripts = [f for f in os.listdir("./scripts/custom") if os.path.isfile('./scripts/custom/'+f)]
    if len(c_scripts) == 0: return
    for j in c_scripts:
        ipath = f'scripts/custom/{j[:-3]}'
        custom_scripts.append(ScriptParser(j[:-3], ipath))
        print(f"[+] Registering Custom Script {j[:-3]}")

def port_thread(thread_idx, port, kwargs):
    p_threads = []
    print(f"[*] Started Thread:{thread_idx} for port {port}")
    try:
        for custom_script in custom_scripts:
            thread = threading.Thread(target=custom_script.run, kwargs=kwargs)
            p_threads.append(thread)

        for p_thread in p_threads:
            p_thread.start()
            p_thread.join()
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

def chk_docker():
    if os.path.exists('/.dockerenv'):
        return True
    return False

def main():
      

    # _, file = nmap_module.create_ps(ip, project_name)
    # ports = nmap_module.get_ports(file)
    # web_ports = web_server_check_module.check_webserver("127.0.0.1", ports, 4)

    # threads = []
    
    # for vport in web_ports:
    #     thread = threading.Thread(target=port_thread, args=(len(threads)+1, vport, wordlist))
    #     threads.append(thread)
    
    # for thread in threads:
    #     thread.start()
    #     thread.join()
    register_default_scripts()
    register_custom_scripts()

    project_name  = input("Enter Project Name:")
    ip = input("Enter IP Address of the WebApp:")
    wordlist = input("Enter Wordlist Path:")

    docker = chk_docker()
    dir = None
    if not docker:
        print("[!] Not Running in a Docker Environment using current directory for creating folders")
        dir = os.getcwd()
    else:
        print("[!] Running in a Docker Container, using Root Directory (/)")
        os.mkdir("/result")
        dir = "/result"
    
    project_directory = dir + f"/{project_name}"
    if not os.path.exists(project_directory):
        os.mkdir(project_directory)
    os.chdir(project_directory)  

    threads = []
    kwargs = {
        'host': ip,
        'n_threads': 4,
        'project_name': project_name,
        'wordlist': wordlist,
        'success_codes':[200,301,302], 
        'filter_codes':[]
    }

    # Run Default Scripts in Sequence
    for default_script in default_scripts:
        retval = default_script.run(**kwargs)
        print(f"Return Value Received from {default_script.name} is : {retval}")
        if retval is not None:
            kwargs.update(retval)

    # Run Custom Scripts Parallely, Custom Scripts will run per port

    ports = kwargs['web_ports']

    for port in ports:
        new_kwargs = dict(kwargs)
        new_kwargs['port'] = port
        new_kwargs['host'] = 'http://'+kwargs['host']
        thread = threading.Thread(target=port_thread, args=(len(threads)+1, port, new_kwargs))
        threads.append(thread)
    
    for t in threads:
        t.start()
        t.join()


if __name__ == "__main__":
    main()