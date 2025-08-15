# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
import random

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

text_type = unicode if PY2 else str

def extract_sid_key(service_line):
    try:
        if not service_line.startswith("1:"):
            return "0:0:0"
        parts = service_line.split(":")
        return "{0}:{1}:{2}".format(parts[3].lower(), parts[4].lower(), parts[5].lower())
    except IndexError:
        return "0:0:0"

def parse_lamedb(filepath="/etc/enigma2/lamedb"):
    freq_map = {}
    if not os.path.exists(filepath):
        return freq_map

    try:
        if PY2:
            import codecs
            f = codecs.open(filepath, "r", encoding='utf-8')
        else:
            f = open(filepath, "r", encoding='utf-8', errors='ignore')
        lines = f.readlines()
        f.close()
    except Exception:
        return freq_map

    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if line.count(":") == 2:
            key = line.lower()
            index += 2
            if index < len(lines):
                freq_line = lines[index].strip()
                parts = freq_line.split()
                if len(parts) >= 2:
                    try:
                        freq = int(parts[1])
                    except ValueError:
                        freq = 0
                    freq_map[key] = freq
            index += 1
        else:
            index += 1
    return freq_map

def sort_services(services, method="alphabetical", lamedb_path="/etc/enigma2/lamedb"):
    if method == "alphabetical":
        services.sort(key=lambda s: s.lower())
    elif method == "random":
        random.shuffle(services)
    elif method == "frequency":
        freq_map = parse_lamedb(lamedb_path)
        services.sort(key=lambda s: freq_map.get(extract_sid_key(s), 0))
    return services
