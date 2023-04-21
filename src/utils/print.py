from colorama import Fore, Style

def print_success(text):
    print(f"{Fore.GREEN}{Style.BRIGHT}[+] {text}{Fore.RESET}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}{Style.BRIGHT}[x] {text}{Fore.RESET}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}{Style.BRIGHT}[!] {text}{Fore.RESET}{Style.RESET_ALL}")

def print_info_dim(text):
    print(f"{Fore.BLUE}{Style.DIM}[-] {text}{Fore.RESET}{Style.RESET_ALL}")

def print_process_step(text, inline=False):
    print(f"{Fore.CYAN}{Style.BRIGHT}[*] {text}{Fore.RESET}{Style.RESET_ALL}", end='\n' if not inline else '\r')