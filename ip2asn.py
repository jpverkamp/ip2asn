#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import urllib.request
import zipfile

# Paths for the data file this module needs.
REMOTE_FILE = 'http://download.maxmind.com/download/geoip/database/asnum/GeoIPASNum2.zip'
LOCAL_ZIP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GeoIPASNum2.zip')
LOCAL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GeoIPASNum2.csv')

# Store data as a list so we can BST it
DATA = []
CENTER = 0

# Verify that an effective TLD file exists. If not, download it.
if not os.path.exists(LOCAL_FILE):
    urllib.request.urlretrieve(REMOTE_FILE, LOCAL_ZIP_FILE)
    with zipfile.ZipFile(LOCAL_ZIP_FILE) as zfin:
        for file in zfin.namelist():
            zfin.extract(file, os.path.dirname(LOCAL_FILE))

# Load the IP -> ASN mapping
# Each line is of the form 'ip min,ip max,ASN'
with open(LOCAL_FILE, 'r', encoding = 'latin-1') as fin:
    for line in fin:
        line = line.strip().split(',', 2)
        if len(line) != 3: continue
        DATA.append((int(line[0]), int(line[1]), line[2].strip('"')))
DATA = list(sorted(DATA))

def ip2asn(ip):
    """
    Lookup the ASN for an IP. 

    IP can be of any of the following forms:
        '192.168.1.1'
        (192, 168, 1, 1)
        3232235777 = 192 * 256^3 + 168 * 256^2 + 1 * 256 + 1

    If no ASN exists for a given IP, None will be returned.
    """

    # Convert possible IP address types
    if isinstance(ip, str): ip = tuple(map(int, ip.split('.')))
    if isinstance(ip, list): ip = tuple(ip)
    if isinstance(ip, tuple): ip = ip[0] * 256 ** 3 + ip[1] * 256 ** 2  + ip[2] * 256  + ip[3] 

    # Lookup the IP using a binary search
    min = 0; max = len(DATA) - 1
    while True:
        mid = (min + max) // 2

        # Found the IP we want, continue
        if DATA[mid][0] <= ip <= DATA[mid][1]:
            return DATA[mid][2]

        # If we're out of bounds, we'll never find one
        # If min == mid and this isn't the correct answer, we're also done
        elif ip < DATA[min][0] or ip > DATA[max][1] or min == mid:
            return None

        # In the lower half
        elif ip < DATA[mid][0]:
            max = mid

        # In the upper half
        elif ip > DATA[mid][1]:
            min = mid

        # This should never happen...
        else:
            raise Exception("Binary search failed")

if __name__ == '__main__':
    for ip in sys.argv[1:]:
        print('{} => {}'.format(ip, ip2asn(ip)))
