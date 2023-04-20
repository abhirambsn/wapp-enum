import logging
import os
from datetime import datetime
from .checks import chk_docker

log_dir = ''

if chk_docker():
    log_dir = '/logs'
else:
    log_dir = '/tmp/logs'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

debug_logger = logging.getLogger(__name__)
debug_logger.addHandler(logging.FileHandler(os.path.join(log_dir, 'wapp-enum_debug.log')))

error_logger = logging.getLogger(__name__)
error_logger.addHandler(logging.FileHandler(os.path.join(log_dir, 'wapp-enum_error.log')))

info_logger = logging.getLogger(__name__)
info_logger.addHandler(logging.FileHandler(os.path.join(log_dir, 'wapp-enum_info.log')))

def debug_log(module, message):
    debug_logger.debug(f"DEBUG:{module}:{datetime.now().isoformat()}:{message}")

def error_log(module, message):
    error_logger.error(f"ERROR:{module}:{datetime.now().isoformat()}:{message}")

def info_log(module, message):
    info_logger.info(f"INFO:{module}:{datetime.now().isoformat()}:{message}")