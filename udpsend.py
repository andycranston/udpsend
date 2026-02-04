#!/usr/bin/python3
#
# @(!--#) @(#) udpsend.py, sversion 0.1.0, fversion 004, 04-february-2026
#
# construct a UDP network packet and send it to a host
#

#
# Links:
# -----
#
#    
#
# Feature list:
# ------------
#
#    oid to bytes
#    snmp encapsulate function (maybe berlength?)
#    variables (save/set - add)
#

##############################################################################

#
# imports
#

import sys
import os
import argparse
import time
import string
import socket
import select

##############################################################################

#
# globals
#

DEFAULT_UDP_SEND_FILE = 'udpsend.txt'

COMMENT_CHAR = '#'

MAX_PACKET_SIZE = 1024000

##############################################################################

def showpacket(bytes, prefix):
    bpr = 16             # bpr is Bytes Per Row
    
    numbytes = len(bytes)

    if numbytes == 0:
        print('{} <empty packet>'.format(prefix))
    else:
        i = 0
        
        while i < numbytes:
            if (i % bpr) == 0:
                print("{} {:04X} :".format(prefix, i), sep='', end='')
                chars = ''
            
            c = bytes[i]
            
            if (c < 32) or (c > 126):
                c = '?'
            else:
                c = chr(c)
            
            chars += c

            print(" {:02X}".format(bytes[i]), sep='', end='')

            if ((i + 1) % bpr) == 0:
                print('    {}'.format(chars))

            i = i + 1

    if (numbytes % bpr) != 0:
        print('{}    {}'.format(' ' * (3 * (bpr - (numbytes % bpr))), chars))

    return

##############################################################################

def isbyteint(s):
    if not s.isdigit():
        return False
    
    b = int(s)
    
    if b < 0:
        return False

    if b > 255:
        return False
        
    return True
    
##############################################################################

def ishexstring(s):
    if len(s) < 4:
        return False
    
    s = s.lower()
    
    if s[0:2] != '0x':
        return False
    
    if (len(s) % 2) != 0:
        return False
    
    for h in s[2:]:
        if not h in string.hexdigits:
            return False
    
    return True

##############################################################################

def isquotedstring(s):
    if len(s) < 3:
        return False
    
    if s[0] != s[-1]:
        return False
    
    if not (s[0] in [ "'", '"' ]):
        return False
    
    return True

##############################################################################

def words2bytes(words, linenum):
    global progname
    
    bytes = []
    
    for word in words:
        if isbyteint(word):
            bytes.append(int(word))
        elif isquotedstring(word):
            for c in word[1:-1]:
                bytes.append(ord(c))
        elif ishexstring(word):
            for i in range(2, len(word), 2):
                bytes.append(int('0x{}'.format(word[i:i+2]), 16))
        else:
            print('{}: badly formed data at line {}'.format(progname, linenum), file=sys.stderr)

    return bytes

##############################################################################

def addbytes(packet, bytes, mode):
    if mode == 'append':
        packet = packet + bytes
    else:
        packet = bytes + packet
        
    return packet

##############################################################################

def process_udp_sendfile(file):
    global progname

    transport = 'udp'
    host = 'localhost'
    port = 7
    packet = bytearray(0)
    mode = 'append'
    timeout = 2.0
    
    aliases = {}
    
    if transport == 'udp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        printf('{}: unsupported transport method "{}" - ("tcp" might be added :-)'.format(progname, transport), file=sys.stderr)
        return
    
    linenum = 0

    for rawline in file:
        linenum += 1
        
        line = rawline.strip()
        
        if len(line) == 0:
            continue
        
        if line[0] == COMMENT_CHAR:
            continue
        
        words = line.split()
        
        if len(words) == 0:
            continue
        
        cmd = words[0].lower()
        
        if cmd in aliases:
            cmd = aliases[cmd]
        
        if cmd == 'exit':
            break
        
        if cmd == 'alias':
            aliases[words[1]] = words[2]
        elif cmd == 'aliases':
            if len(aliases) == 0:
                print('<none>')
            else:
                for a in aliases:
                    print('{} => {}'.format(a, aliases[a]))
        elif cmd == 'host':
            host = words[1]
        elif cmd == 'port':
            port = int(words[1])
        elif cmd == 'prepend':
            mode = 'prepend'
        elif cmd == 'append':
            mode = 'append'
        elif cmd == 'null':
            packet = bytearray(0)
        elif cmd == 'timeout':
            timeout = float(words[1])
        elif cmd == 'fill':
            for i in range(0, int(words[1])):
                packet = addbytes(packet, bytearray(words2bytes(words[2:], linenum)), mode)
        elif cmd == 'length-1byte':
            packet = addbytes(packet, bytearray([len(packet)]), mode)
        elif cmd == 'sleep':
            time.sleep(float(words[1]))                
        elif cmd == 'show':
            showpacket(packet, '>')
        elif cmd == 'send':
            sock.sendto(packet, (host, port))
        elif cmd == 'receive':
            ready, dummy1, dummy2 = select.select([sock], [], [], timeout)    
            if len(ready) == 0:
                print('{}: timeout on receive packet - waited {} seconds'.format(progname, timeout), file=sys.stderr)
            else:
                inpacket, server = sock.recvfrom(MAX_PACKET_SIZE)
                showpacket(inpacket, '<')            
        else:
            packet = addbytes(packet, bytearray(words2bytes(words, linenum)), mode)
    
    sock.close()
    
    return

##############################################################################

def main():
    global progname
    
    parser = argparse.ArgumentParser()
        
    parser.add_argument('-f',
                        '--file',
                        help='name of UDP send file (default is "{}")'.format(DEFAULT_UDP_SEND_FILE),
                        default=DEFAULT_UDP_SEND_FILE)

    args = parser.parse_args()
    
    filename = args.file
    
    try:
        file = open(filename, 'r', encoding='utf=8')
    except IOError:
        print('{}: unable to open UDP send file "{}" for reading'.format(progname, filename), file=sys.stderr)
        sys.exit(1)
    
    process_udp_sendfile(file)
    
    file.close()
    
    return 0

##############################################################################

progname = os.path.basename(sys.argv[0])

sys.exit(main())

# end of file
