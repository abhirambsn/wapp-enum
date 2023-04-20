import requests
import threading
from utils.print import print_success, print_error, print_process_step
from utils.logger import info_log, error_log

def check_vhost(host, port, vhost):
    domain = host[5:]
    
    try:
        url = "http://{vhost}:{domain}:{port}"
        print_process_step(f"Hitting url: {url}")
        r = requests.get(url)
        if r.status_code == 200:
            return True, f"{vhost}.{domain}", port
        return False, None, None
    except Exception as e:
        print_error(f"[x] Error: {str(e)}")
        return False, None, None

def enumerate_batch(thread_idx, host, port, vhost_list, start=0, batch_size=1):
    info_log(__name__, f"Thread with index {thread_idx} has started")
    vhosts = vhost_list[start:start+batch_size]
    for vhost in vhosts:
        found, url, port  = check_vhost(host, port, vhost)
        if found:
            print_success(f"[+] Found vhost: {vhost} URL: {url} Port: {port}")


def run(host, port, vhost_path, n_threads=4):
    vhost_list = open(vhost_path, 'r').readlines()
    t_count = n_threads
    if (len(vhost_list) < n_threads):
        t_count = len(vhost_list)

    batch_size = len(vhost_list) // t_count
    threads = []
    
    for i in range(t_count):
        t = threading.Thread(target=enumerate_batch, args=(i, host, port, vhost_list, len(vhost_list)*i, batch_size))
        threads.append(t)
    
    for t in threads:
        t.start()
        t.join()
    
    print_success(f"[+] Virtual host enumeration completed for Host: {host} and Port: {port}")
    