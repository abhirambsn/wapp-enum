import requests
import threading
import os
from utils.print import print_success, print_error, print_process_step
from utils.logger import info_log, error_log

from concurrent.futures import ThreadPoolExecutor, as_completed

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

def enumerate_batch(batch_idx, hostname, port, batch, result_file_handler, n_threads=4):
    info_log(__name__, f"Batch {batch_idx} with has started Enumeration")
    print_process_step(f"Queued Batch {batch_idx} for Virtual Host Enumeration")
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        proc = {executor.submit(check_vhost, hostname, port, vhost): vhost for vhost in batch}
        for future in as_completed(proc):
            try:
                found, url, port = future.result()
                if found:
                    print_success(f"Found vhost: {url} Port: {port}")
                    file_lock.acquire()
                    result_file_handler.write(f"Vhost: {url}\tPort: {port}\r\n")
                    file_lock.release()
            except Exception as e:
                print_error(f"Error: {str(e)}")
    # for vhost in vhosts:
    #     vhost = vhost.strip('\n')
    #     found, url, port  = check_vhost(hostname, port, vhost)
    #     if found:
    #         print_success(f"Found vhost: {vhost} URL: {url} Port: {port}")
    #         file_lock.acquire()
    #         result_file_handler.write(f"Vhost: {url}\tPort: {port}\r\n")
    #         file_lock.release()


def run(hostname, port, vhost_path, n_threads=4):
    vhost_list = open(vhost_path, 'r').readlines()
    t_count = n_threads
    if (len(vhost_list) < n_threads):
        t_count = len(vhost_list)

    batch_size = len(vhost_list) // t_count
    batches = [vhost_list[i:i+batch_size] for i in range(0, len(vhost_list), batch_size)]
    # threads = []

    mode = 'a' if os.path.exists(os.getcwd() + f"/vhost_enum_{hostname}.txt") else 'w'
    rf_handler = open(f"./vhost_enum_{hostname}.txt", mode)
    
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        batch_proc = {executor.submit(enumerate_batch, i+1, hostname, port, batches[i], rf_handler): i for i in range(len(batches))}

        for future in as_completed(batch_proc):
            try:
                future.result()
            except Exception as e:
                print_error(f"Parent Thread Error: {str(e)}")

    # for i in range(t_count):
    #     t = threading.Thread(target=enumerate_batch, args=(i, hostname, port, vhost_list, rf_handler, len(vhost_list)*i, batch_size))
    #     threads.append(t)
    
    # for t in threads:
    #     t.start()
    #     t.join()
    
    print_success(f"Virtual host enumeration completed for Host: {hostname} and Port: {port}")
    rf_handler.close()