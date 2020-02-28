#!/usr/bin/env python

import sys
import os
import subprocess
import click

def enable_event(event):
    f = open("/sys/kernel/debug/tracing/events/%s/enable"%event, mode='w')
    f.write('1')
    f.close()

def disable_event(event):
    f = open("/sys/kernel/debug/tracing/events/%s/enable"%event, mode='w')
    f.write('0')
    f.close()
    
def set_trace_buffer_size(buffer_size_kb):
    subprocess.call("echo %d > /sys/kernel/debug/tracing/buffer_size_kb"%buffer_size_kb,
                    shell=True)

def set_trace_filter(event, filter_string):
    f = open("/sys/kernel/debug/tracing/events/%s/filter"%event, mode='w')
    f.write(filter_string)
    f.close()
    
def clear_trace_buffer():
    subprocess.call('echo "" > /sys/kernel/debug/tracing/trace', shell=True)

def validate_filter(ctx, param, filter_string):
    # TODO: actually validate the filter string
    return filter_string

@click.group()
def cli():
    pass

@cli.command()
@click.option('--output-dir', default=None, type=click.Path(exists=True))
@click.option('--normalize-time/--raw-time', default=True, help="Show time from beginning of trace/wall-clock time")
@click.argument('trace_path', metavar='trace', type=click.Path(exists=True))
def plot(output_dir, normalize_time, trace_path):
    """Generate plots from a TCP trace"""
    import tcp_probe.plot
    tcp_probe.plot.plot_trace(output_dir, trace_path, normalize_time)
    
@cli.command()
@click.option('--clear/--no-clear', default=True, help="Whether to clear the kernel trace buffer before starting the trace")
@click.option('-b', '--buffer', 'buffer_size', default=500000, help="Size of trace buffer in kb")
@click.argument('filter_string', metavar='filter', default='0', callback=validate_filter)
def trace(clear, buffer_size, filter_string):
    """Takes a tcp-related trace from the Linux kernel.

    Takes an optional filter for the kernel trace. Please see the kernel documentation for syntax: https://www.kernel.org/doc/html/latest/trace/events.html#event-filtering
    """
    events = [
        "tcp"
    ]
    
    try:
        for event in events:
            set_trace_filter(event, filter_string)
            enable_event(event)
    except PermissionError as e:
        print("error: insufficient permissions to enable event tracing", file=sys.stderr)
        sys.exit(1)

    set_trace_buffer_size(buffer_size)

    if clear:
        clear_trace_buffer()

    try:
        print(flush=True)
        subprocess.call('cat /sys/kernel/debug/tracing/trace_pipe', shell=True)
    finally:
        for event in events:
            disable_event(event)
            set_trace_filter(event, "0")
