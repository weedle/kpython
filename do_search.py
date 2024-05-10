#!/usr/bin/python3
import os
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

path = os.path.dirname(os.path.realpath(__file__))

colorama_init()

COLORS = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.RED, Fore.YELLOW]
param_colors = {}

def search_in_files(args, files):
    lines = set()
    for arg in args:
        try:
            if arg != None:
                arg = arg.strip()
                procArgs = ["grep", arg, "-Hrn"] + list(files)
                proc = str(subprocess.check_output(procArgs, universal_newlines=True))
                for line in proc.split('\n'):
                    lines.add(line.strip())
        except subprocess.CalledProcessError:
            print("No results.")

    lines = list(lines)
    lines.sort(key=sort_by_line_number)
    return lines

def find_files(args):
    global param_colors
    param_colors = {}
    i = 0
    fileSets = []

    for arg in args:
        i += 1
        param_colors[arg] = COLORS[i % len(COLORS)]
        try:
            # First we want to find all files that mention any of the params
            path = os.getcwd()
            proc = str(subprocess.check_output(["grep", arg, "-rl", path], universal_newlines=True))
            files = set()
            for file in proc.split('\n'):
                if file != '':
                    files.add(file.strip())
            fileSets.append(files)
        except subprocess.CalledProcessError:
            print(f"No results for {arg}, removing from search.")

    if len(fileSets) == 0:
        print("No results include all args.")
        exit(0)

    files = fileSets[0]

    for fileSet in fileSets[1:]:
        files = files & fileSet

    return files

def do_search(args):
    f = open(path + "/.TEMP_ARG_LIST", "w")
    for arg in args:
        f.write(f"{arg}\n")
    f.close()
    files = find_files(args)
    return search_in_files(args, files)

def print_results(lines):
    for line in lines:
        for param in param_colors.keys():
            bits = line.split(':')
            if len(bits) >= 2:
                    file = Fore.MAGENTA + bits[0] + Fore.RESET
                    number = Fore.WHITE + bits[1] + Fore.RESET
                    line = ':'.join(bits[2:])
                    line = file + ":" + number + ":" + line.replace(param, param_colors[param] + param + Fore.RESET)
        print(line)

def save_files(lines):
    f = open(path + "/.TEMP_FILE_LIST", "w")
    files = []
    for line in lines:
        file = line.split(':')[0]
        if len(file) > 0 and file not in files:
            files.append(file)
    files = list(files)
    for i in range(len(files)):
        print(f"{i}. {files[i]}")
        f.write(f"{i}. {files[i]}\n")
    f.close()

def list_files():
    f = open(path + "/.TEMP_FILE_LIST", "r")
    lines = f.readlines()
    for line in lines:
        print(line.strip())
    f.close()

def get_file(i):
    f = open(path + "/.TEMP_FILE_LIST", "r")
    file = ""
    lines = f.readlines()
    try:
        i = int(i)
        lines[i]
        file = ".".join(lines[i].split(".")[1:]).strip()
    except Exception as e:
        print(e)
    finally:
        f.close()
    return file

def get_args():
    global param_colors
    try:
        f = open(path + "/.TEMP_ARG_LIST", "r")
        lines = f.readlines()
        i = 0
        for line in lines:
            if line != '':
                arg = line.strip()
                i += 1
                param_colors[arg] = COLORS[i % len(COLORS)]
        return " ".join(lines)
    except Exception as e:
        print(e)

def open_file(i):
    file = get_file(i)
    subprocess.run(["vim", file])

if len(sys.argv) > 2:
    if sys.argv[1] == "s":
        lines = do_search(sys.argv[2:])
        save_files(lines)
        print_results(lines)
    elif sys.argv[1] == "v":
        open_file(sys.argv[2])
    elif sys.argv[1] == "fs":
        lines = search_in_files([get_args()], [get_file(sys.argv[2])])
        remove_name = lambda s: " ".join(s.split(":")[1:])
        #lines = map(remove_name, lines)
        print_results(lines)
elif len(sys.argv) == 2:
    if sys.argv[1] == "fl":
        list_files()
