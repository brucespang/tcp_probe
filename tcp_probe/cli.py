#!/usr/bin/env python

import sys
import subprocess
import click
from .trace import *


@click.group()
def cli():
    pass


@cli.command()
@click.option("--output-dir", default=None, type=click.Path(exists=True))
@click.option("--open/--no-open", "open_result", default=False)
@click.option(
    "--normalize-time/--raw-time",
    default=True,
    help="Show time from beginning of trace/wall-clock time",
)
@click.argument("trace_path", metavar="trace", type=click.Path(exists=True))
def plot(output_dir, open_result, normalize_time, trace_path):
    """Generate plots from a TCP trace"""
    import tcp_probe.plot

    result_path = tcp_probe.plot.plot_trace(output_dir, trace_path, normalize_time)

    if open_result:
        subprocess.check_call("open %s" % (result_path), shell=True)


@cli.command()
@click.option(
    "--clear/--no-clear",
    default=True,
    help="Whether to clear the kernel trace buffer before starting the trace",
)
@click.option(
    "-b", "--buffer", "buffer_size", default=500000, help="Size of trace buffer in kb"
)
@click.argument("filter_string", metavar="filter", default="0")
def trace(clear, buffer_size, filter_string):
    """Takes a tcp-related trace from the Linux kernel.

    Takes an optional filter for the kernel trace. Please see the kernel documentation for syntax: https://www.kernel.org/doc/html/latest/trace/events.html#event-filtering
    """
    events = ["tcp"]

    try:
        for event in events:
            set_trace_filter(event, filter_string)
            enable_event(event)
    except PermissionError:
        print(
            "error: insufficient permissions to enable event tracing", file=sys.stderr
        )
        sys.exit(1)

    set_trace_buffer_size(buffer_size)

    if clear:
        clear_trace_buffer()

    enable_tracing()

    try:
        print(flush=True, end="")

        p = start_trace(sys.stdout)
        p.communicate()
    finally:
        for event in events:
            disable_event(event)
            set_trace_filter(event, "0")
