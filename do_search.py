#!/usr/bin/python3
import subprocess
import sys

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

def sort_by_line_number(line):
    bits = line.split(':')
    if len(bits) >= 2 and len(bits[1]) > 0:
        return len(bits[0]) * 10000 + int(bits[1])
    else:
        return 0

colorama_init()

lines = set()
COLORS = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.RED, Fore.YELLOW]
param_colors = {}

i = 0
for arg in sys.argv[1:]:
    i += 1
    param_colors[arg] = COLORS[i % len(COLORS)]
    try:
        proc = str(subprocess.check_output(["grep", arg, "-rn"], universal_newlines=True))
        for line in proc.split('\n'):
            lines.add(line.strip())
    except subprocess.CalledProcessError:
        print("No results.")

#proc = str(proc).replace(arg, f"{Fore.BLUE}{arg}{Style.RESET_ALL}")

lines = list(lines)
lines.sort(key=sort_by_line_number)

for line in lines:
    for param in param_colors.keys():
        bits = line.split(':')
        if len(bits) >= 2:
                file = Fore.MAGENTA + bits[0] + Fore.RESET
                number = Fore.WHITE + bits[1] + Fore.RESET
                line = ':'.join(bits[2:])
                line = file + ":" + number + ":" + line.replace(param, param_colors[param] + param + Fore.RESET)
    print(line)
