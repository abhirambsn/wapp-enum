import threading
import requests
import sys
import os

from utils.print import print_success, print_error, print_process_step

file_lock = threading.Lock()

def request_url(url, path, success_codes=[200,301,302], filter_codes=[]):
    try:
        r = requests.get(url+'/'+path.strip('\n'))
        status_code = r.status_code

        if status_code in filter_codes:
            return False, None, None
        
        if status_code in success_codes:
            return True, status_code, url+"/"+path
        else:
            return False, None, None
    except requests.ConnectionError as e:
        print_error(f"Connection Error")
        sys.exit(-1)
        

def threaded_request(thread_index, res_file, host, wordlist, success_codes=[200,301,302], filter_codes=[], batch_size=100, start=0):
    batch = wordlist[start: start+batch_size]
    for path in batch:
        path_striped = path.strip('\n')
        req = request_url(host, path_striped, success_codes, filter_codes)
        if req[0]:
            print_success(f"[Thread: {thread_index}] Found: {req[2]}\tStatus Code: {req[1]}")
            file_lock.acquire()
            res_file.write(f"{req[2]}\t\tCode:{req[1]}\r\n")
            file_lock.release()

def run(host, port, wordlist="", n_threads=4, success_codes=[200,301,302], filter_codes=[]):
    if not os.path.exists(os.getcwd() + "/directory_enum"):
        os.mkdir(os.getcwd() + "/directory_enum")
    mode = 'a' if os.path.exists(os.getcwd() + f"/directory_enum/result_{port}.txt") else 'w'
    f = open(f"directory_enum/result_{port}.txt", mode)
    wordlist_file = open(wordlist, 'r').readlines()
    batch_size = len(wordlist_file) // n_threads
    if batch_size < 1:
        batch_size = len(wordlist_file)
    thread_pool = []
    for i in range(n_threads):
        url = host + ":" + str(port)
        thread = threading.Thread(target=threaded_request, args=(i+1, f, url, wordlist_file, success_codes, filter_codes, batch_size, len(wordlist_file)*i))
        thread_pool.append(thread)
    
    for thread in thread_pool:
        thread.start()
        thread.join()
    
    f.close()
    print_process_step(f"Processed {len(wordlist)} paths")
    print_success(f"Directory Enumeration Done")