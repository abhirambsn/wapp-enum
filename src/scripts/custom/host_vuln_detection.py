import subprocess
import os

from utils.print import print_success, print_error

def run(host, port):
    cmd = ["nikto", '-h', host+":"+str(port)]
    if not os.path.exists(os.getcwd() + "/nikto"):
        os.mkdir(os.getcwd() + "/nikto")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if len(stderr.decode()) > 0:
        print_error(f"Error Occurred during scan!! [ERROR]: {stderr.decode()}")
        return
    output_file = f"nikto_{port}.scan"
    with open(f"nikto/{output_file}", 'w') as writer:
        writer.write(stdout.decode('utf-8'))
    print_success(f"Scan Done, Results are saved to: {output_file}")