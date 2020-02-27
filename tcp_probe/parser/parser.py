import re
import sys
import os
import gzip

def open_trace(f):
    path = os.path.dirname(f)
    filename = os.path.basename(f)
    if '.gz' in filename:
        lines = list(gzip.open(f))
    else:
        lines = list(open(f))
    return lines

def parse_tcp_probe_line(line):
    if "tcp_probe" not in line:
        return None
    
    match = re.match(".*\s(.*): tcp_probe: (.*)", line.strip())
    if match is None:
        return None
    
    timestamp = float(match.group(1))
    data = {pair.split('=')[0]:pair.split('=')[1] for pair in match.group(2).split(' ')}
    integer_fields = ['rcv_wnd', 'snd_cwnd', 'snd_wnd', 'srtt', 'ssthresh', 'data_len']
    for f in integer_fields:
        try:
            data[f] = int(data[f])
        except:
            print(f)
            
    hex_fields = ['snd_nxt', 'snd_una', 'mark']
    for f in hex_fields:
        data[f] = int(data[f], 16)
        data['timestamp'] = timestamp

    data['sport'] = int(data['src'].split(':')[-1])
    data['dport'] = int(data['dest'].split(':')[-1])
    
    return data

def parse_tcp_retransmit_skb_line(line):
    if "tcp_retransmit_skb" not in line:
        return None
    
    match = re.match(".*\s(.*): tcp_retransmit_skb: (.*)", line.strip())
    if match is None:
        return None
    
    timestamp = float(match.group(1))
    data = {pair.split('=')[0]:pair.split('=')[1] for pair in match.group(2).split(' ')}
    integer_fields = ['sport', 'dport']
    for f in integer_fields:
        try:
            data[f] = int(data[f])
        except:
            print(f)
    data['timestamp'] = timestamp
    return data
