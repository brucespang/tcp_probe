import pandas as pd
import plorts
import numpy as np
import matplotlib.pyplot as plt
import re
import sys
import os
import gzip
from collections import defaultdict
import tcp_probe.parser as parser
plt.style.use(['plorts','plorts-print'])

def plot_trace(output_dir, trace_path, normalize_time):
    trace_dir = os.path.dirname(trace_path)
    trace_file = os.path.basename(trace_path)

    lines = parser.open_trace(trace_path)

    rows = [parser.parse_tcp_probe_line(line) for line in lines]
    rows = [r for r in rows if r is not None]
    df = pd.DataFrame(rows)

    xmin,xmax=df.timestamp.min(), df.timestamp.max()

    if normalize_time:
        df['timestamp'] = df['timestamp'] - xmin
        xlabel = "Timestamp (sec)"
    else:
        xlabel = "Timestamp"
        
    num_plots = 3
    
    plt.figure(figsize=(18,15))
    plt.subplot(num_plots,1,1)
    plt.title("snd_cwnd")
    plorts.scatter(df, x="timestamp", y="snd_cwnd", hue=["sport", "dport"])
    plt.xlabel(xlabel)
    plt.legend(loc='best')

    plt.subplot(num_plots,1,2)
    plt.title("srtt")
    plorts.scatter(df, x="timestamp", y="srtt", hue=["sport", "dport"])
    plt.axis(xmin=xmin, xmax=xmax)
    plt.xlabel(xlabel)
    plt.legend(loc='best')

    plt.subplot(num_plots,1,3)
    rows = [parser.parse_tcp_retransmit_skb_line(line) for line in lines]
    rows = [r for r in rows if r is not None]
    df = pd.DataFrame(rows)
    
    if len(df) > 0:
        if normalize_time:
            df['timestamp'] = df['timestamp'] - xmin

        flow_ids = {}
        for sport in df.sport.unique():
            flow_ids[sport] = len(flow_ids)
        df["flow_id"] = [flow_ids[sport] for sport in df.sport]

        plt.title("retransmitted skbs")
        plorts.scatter(df, x="timestamp", y="flow_id", hue="sport")
        plt.axis(xmin=xmin, xmax=xmax)
        plt.xlabel(xlabel)

    if output_dir is None:
        output_path = '%s.png'%(trace_path)
    else:
        output_path = os.path.join(trace_dir, output_dir, '%s.png'%(trace_file))

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
