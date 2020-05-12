import re
import sys
import os
import gzip
import io
import pandas as pd

def open_trace(f, iterator=False):
    path = os.path.dirname(f)
    filename = os.path.basename(f)
    if '.gz' in filename:
        lines = io.TextIOWrapper(gzip.open(f))
    else:
        lines = open(f)
        
    if iterator:
        return lines
    else:
        return list(lines)

def parse_generic_line(line, integer_fields=set(), hex_fields=set()):
    fields = line.strip().split()
    timestamp = float(fields[3].replace(':', ''))
    data = {}

    for pair in fields[5:]:
        k,v = pair.split('=')
        if k in integer_fields:
            v = int(v)
        elif k in hex_fields:
            v = int(v, 16)
        data[k] = v
            
    data['timestamp'] = timestamp
    
    return data

def parse_tcp_probe_line(line):
    if "tcp_probe" not in line:
        return None

    integer_fields = set(['rcv_wnd', 'snd_cwnd', 'snd_wnd', 'srtt', 'ssthresh', 'data_len'])
    hex_fields = set(['snd_nxt', 'snd_una', 'mark'])
    
    data = parse_generic_line(line, integer_fields, hex_fields)
    
    data['sport'] = int(data['src'].split(':')[-1])
    data['dport'] = int(data['dest'].split(':')[-1])
    
    return data

def parse_tcp_retransmit_skb_line(line):
    if "tcp_retransmit_skb" not in line:
        return None
    
    data = parse_generic_line(line, integer_fields=set(['sport', 'dport']))
    return data

def parse_trace(f):
    lines = open_trace(f, iterator=True)

    tcp_probe_rows = []
    retrans_rows = []
    
    for line in lines:
        try:
            if "tcp_probe" in line:
                tcp_probe_rows.append(parse_tcp_probe_line(line))
            elif "tcp_retransmit_skb" in line:
                retrans_rows.append(parse_tcp_retransmit_skb_line(line))
        except:
            print("Exception parsing line:\n", line, "\n", sys.exc_info()[0])

    return pd.DataFrame(tcp_probe_rows), pd.DataFrame(retrans_rows)
