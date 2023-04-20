import requests
import threading
import os
from utils.print import print_success, print_error, print_process_step
from utils.logger import info_log, error_log

file_lock = threading.Lock()

def check_vhost(hostname, port, vhost):
    try:
        url = f"http://{vhost}.{hostname}"
        print_process_step(f"Hitting url: {url}")
        r = requests.get(url)
        if r.status_code == 200:
            return True, url, port
        return False, None, None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False, None, None

def enumerate_batch(thread_idx, hostname, port, vhost_list, result_file_handler, start=0, batch_size=1):
    info_log(__name__, f"Thread with index {thread_idx} has started")
    vhosts = vhost_list[start:start+batch_size]
    for vhost in vhosts:
        vhost = vhost.strip('\n')
        found, url, port  = check_vhost(hostname, port, vhost)
        if found:
            print_success(f"Found vhost: {vhost} URL: {url} Port: {port}")
            file_lock.acquire()
            result_file_handler.write(f"Vhost: {url}\tPort: {port}\r\n")
            file_lock.release()


def run(hostname, port, vhost_path, n_threads=4):
    vhost_list = open(vhost_path, 'r').readlines()
    t_count = n_threads
    if (len(vhost_list) < n_threads):
        t_count = len(vhost_list)

    batch_size = len(vhost_list) // t_count
    threads = []

    mode = 'a' if os.path.exists(os.getcwd() + f"/vhost_enum_{hostname}.txt") else 'w'
    rf_handler = open(f"./vhost_enum_{hostname}.txt", mode)
    
    for i in range(t_count):
        t = threading.Thread(target=enumerate_batch, args=(i, hostname, port, vhost_list, rf_handler, len(vhost_list)*i, batch_size))
        threads.append(t)
    
    for t in threads:
        t.start()
        t.join()
    
    print_success(f"Virtual host enumeration completed for Host: {hostname} and Port: {port}")
    rf_handler.close()