import threading
import requests
import sys

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
        print(f"Connection Error")
        sys.exit(-1)
        

def threaded_request(thread_index, host, wordlist, success_codes=[200,301,302], filter_codes=[], batch_size=100, start=0):
    batch = wordlist[start: start+batch_size]
    print(f"Thread Index: {thread_index} Starting from {start} to {start+batch_size}")
    for path in batch:
        path_striped = path.strip('\n')
        req = request_url(host, path_striped, success_codes, filter_codes)
        if req[0]:
            print(f"[+] Found: {req[2]}\tStatus Code: {req[1]}")

def run(host, port, wordlist="", n_threads=4, success_codes=[200,301,302], filter_codes=[]):
    wordlist_file = open(wordlist, 'r').readlines()
    batch_size = len(wordlist_file) // n_threads
    if batch_size < 1:
        batch_size = len(wordlist_file)
    thread_pool = []
    for i in range(n_threads):
        url = host + ":" + str(port)
        thread = threading.Thread(target=threaded_request, args=(i+1, url, wordlist_file, success_codes, filter_codes, batch_size, len(wordlist_file)*i))
        thread_pool.append(thread)
    
    for thread in thread_pool:
        thread.start()
        thread.join()
    
    print(f"[-] Processed {len(wordlist)} paths")