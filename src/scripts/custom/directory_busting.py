import threading
import requests
import sys
import os
import time

from concurrent.futures import ThreadPoolExecutor, as_completed
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
        

def threaded_request(batch_id, res_file, host, wordlist, success_codes=[200,301,302], filter_codes=[], n_threads=4):
    print_process_step(f"Processing Batch {batch_id}")
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        future_urls = {executor.submit(request_url, host, path.strip('\n'), success_codes, filter_codes): path for path in wordlist}
        for future in as_completed(future_urls):
            try:
                (found, url, code) = future.result()
                if found:
                    print_success(f"Found: {url}\tStatus Code: {code}")
                    file_lock.acquire()
                    res_file.write(f"{url}\t\tCode:{code}\r\n")
                    file_lock.release()
            except Exception as e:
                print_error(f"ERROR: {str(e)}")
    # for path in wordlist:
    #     path_striped = path.strip('\n')
    #     req = request_url(host, path_striped, success_codes, filter_codes)
    #     if req[0]:
    #         print_success(f"[Thread: {thread_index}] Found: {req[2]}\tStatus Code: {req[1]}")
    #         file_lock.acquire()
    #         res_file.write(f"{req[2]}\t\tCode:{req[1]}\r\n")
    #         file_lock.release()

def run(host, port, wordlist="", n_threads=4, success_codes=[200,301,302], filter_codes=[]):
    if not os.path.exists(os.getcwd() + "/directory_enum"):
        os.mkdir(os.getcwd() + "/directory_enum")
    mode = 'a' if os.path.exists(os.getcwd() + f"/directory_enum/result_{port}.txt") else 'w'
    f = open(f"directory_enum/result_{port}.txt", mode)
    wordlist_file = open(wordlist, 'r').readlines()
    batch_size = len(wordlist_file) // n_threads

    if batch_size < 1:
        batch_size = len(wordlist_file)
    
    batches = [wordlist_file[i:i+batch_size] for i in range(0, len(wordlist_file), batch_size)]
    # thread_pool = []

    init_time = time.time()
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        url = host + ":" + str(port)
        batch_proc = {executor.submit(i+1, threaded_request, f, url, batches[i], success_codes, filter_codes): i for i in range(len(batches))}

        for proc in as_completed(batch_proc):
            try:
                proc.result()
            except Exception as e:
                print_error(f"Parent Thread Error: {str(e)}")
    
    end_time = time.time()

    # for i in range(n_threads):
    #     url = host + ":" + str(port)
    #     thread = threading.Thread(target=threaded_request, args=(i+1, f, url, wordlist_file, success_codes, filter_codes, batch_size, len(wordlist_file)*i))
    #     thread_pool.append(thread)
    
    # for thread in thread_pool:
    #     thread.start()
    #     thread.join()
    
    f.close()
    print_process_step(f"Processed {len(wordlist_file)} paths")
    print_success(f"Directory Enumeration Done, Time Taken: {end_time - init_time}")