import os

def chk_docker():
    if os.path.exists('/.dockerenv'):
        return True
    return False