import socket
import threading

class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        super().__init__(group, target, name, args, kwargs)
        self._return_value = None
    
    def run(self):
        if self._target is not None:
            self._return_value = self._target(*self._args, **self._kwargs)
    
    def join(self, *args):
        super().join(*args)
        return self._return_value

def check_port(host, port):
    sock = socket.socket()
    sock.settimeout(1)

    try:
        sock.connect((host, port))
        sock.send(f'GET / HTTP/1.1\r\nHost: {host}\r\n\r\n'.encode())
        data = sock.recv(1024)

        if data.decode().split('\n')[0].startswith("HTTP"):
            sock.close()
            return True, port
    except:
        return False, port
    
    sock.close()

    return False, port


def check_batch(host, ports=[]):
    results = []
    for port in ports:
        (status, port_val) = check_port(host, port)
        if status:
            print(f"[+] Port {port_val} is a WebServer")
            results.append(port_val)
    return results

def run(host, ports_list=[80, 443], n_threads=1):
    results = []
    threads = []
    
    t_count = n_threads
    if len(ports_list) < n_threads:
        t_count = len(ports_list)

    batch_size = len(ports_list) // t_count

    for i in range(t_count):
        port_list = ports_list[i * batch_size : (i + 1) * batch_size]
        t = ThreadWithReturnValue(target=check_batch, args=(host, port_list))
        threads.append(t)
    
    for thread in threads:
        thread.start()
        res = thread.join()
        results.extend(res)
    
    print(f"[+] Valid Web Server Ports are: {results}")
    return {'web_ports': results}
