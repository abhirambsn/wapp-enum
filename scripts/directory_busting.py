import threading
import requests
import sys

def request_url(url, path, success_codes=[200,301,302], filter_code=[]):
    try:
        r = requests.get(url+'/'+path.strip('\n'))
        status_code = r.status_code

        if status_code in filter_code:
            return False, None, None
        
        if status_code in success_codes:
            return True, status_code, url+"/"+path
        else:
            return False, None, None
    except requests.ConnectionError as e:
        print(f"Connection Error")
        sys.exit(-1)
        

def threaded_request(thread_index, host, wordlist, success_codes=[200,301,302], filter_code=[], batch_size=100, start=0):
    batch = wordlist[start: start+batch_size]
    print(f"Thread Index: {thread_index} Starting from {start} to {start+batch_size}")
    for path in batch:
        path_striped = path.strip('\n')
        req = request_url(host, path_striped, success_codes, filter_code)
        print(f"Trying Word: {path_striped}")
        if req[0]:
            print(f"Found: {req[2]}\tStatus Code: {req[1]}")

def directory_busting(host, wordlist_path="", threads=4, success_codes=[200,301,302], filter_codes=[]):
    wordlist = open(wordlist_path, 'r').readlines()
    batch_size = len(wordlist) // threads
    if batch_size < 1:
        batch_size = len(wordlist)
    thread_pool = []
    for i in range(threads):
        thread = threading.Thread(target=threaded_request, args=(i+1, host, wordlist, success_codes, filter_codes, batch_size, len(wordlist)*i))
        thread_pool.append(thread)
    
    for thread in thread_pool:
        thread.start()
        thread.join()