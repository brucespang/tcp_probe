# tcp_probe

A Python library and command-line tool for tracing and analyzing TCP connections in Linux using the kernel's `tcp_probe` functionality.

## What is tcp_probe?

The Linux kernel has [TCP tracepoints](https://www.brendangregg.com/blog/2018-03-22/tcp-tracepoints.html) that provide visibility into TCP connection behavior. These tracepoints expose internal TCP stack metrics that are otherwise difficult or impossible to observe from userspace.

**How it works**: The `tcp:tcp_probe` tracepoint fires on TCP stack events - typically when packets are sent or ACKs are received. Each event captures the current state of TCP variables like congestion window size, RTT measurements, sequence numbers, and window sizes. This gives you a detailed view of how TCP congestion control and flow control are behaving throughout a connection's lifetime.

## Why use this tool?

Understanding network performance can be hard, but it's often easier when you can see exactly what TCP is actually doing internally. This tool makes it easier to access to kernel-level TCP metrics that help answer questions like:

- **How is TCP congestion control behaving?** - Observe congestion window changes on every packet send/ACK receive
- **Why is my connection slow?** - See congestion window evolution, RTT measurements, and retransmission patterns
- **Is my network lossy?** - Track packet retransmissions and their timing
- **What's happening during connection establishment?** - Monitor TCP state transitions and window scaling

### Quick Example
```bash
# Start tracing HTTP connections
sudo tcp_probe trace "sport == 80 || dport == 80" > http_trace.log

# In another terminal, generate some traffic
curl http://example.com

# Stop tracing (Ctrl+C), then visualize
tcp_probe plot http_trace.log
```
This gives you plots showing exactly how TCP's congestion window evolved, RTT measurements, and any retransmissions.

## Overview

This tool makes it easier to capture, parse, and visualize TCP connection data from the Linux kernel's [ftrace infrastructure](https://www.kernel.org/doc/html/latest/trace/ftrace.html). It provides tools to:

- **Trace** TCP events as they occur using Linux kernel's ftrace system
- **Parse** kernel trace output for tcp_probe and tcp_retransmit_skb events  
- **Visualize** TCP metrics like congestion window, round-trip time, and retransmissions

## Installation

```bash
pip install tcp_probe
```

### Dependencies

The dependencies for plotting are `matplotlib, numpy, plorts`. They are not dependencies of the package to avoid needing to install matplotlib/pandas/etc... on whatever system you are tracing. Perhaps there are better ways to do this and PRs are welcome!

## Usage

### Command Line Interface

#### Tracing TCP Connections

Capture TCP events from the kernel (requires root privileges):

```bash
# Basic trace - captures all TCP events
sudo tcp_probe trace

# Trace with filter - only connections on port 80
sudo tcp_probe trace "sport == 80 || dport == 80"

# Custom buffer size and no clearing
sudo tcp_probe trace --buffer 1000000 --no-clear
```

**Trace Filtering**: Use Linux kernel [ftrace filter syntax](https://www.kernel.org/doc/html/latest/trace/events.html#event-filtering) to capture only specific connections. Filters can match on IP addresses, ports, connection states, and more.

**Trace Buffer**: The kernel uses a circular buffer to store trace events. The default size is 500KB, but for high-traffic systems or long traces, you may need a larger buffer (e.g., `--buffer 2000000` for 2GB). Use `--no-clear` to append to existing trace data rather than starting fresh.

The trace command captures:
- **tcp_probe events**: Fired on TCP stack activity (packet sends/ACK receives), capturing congestion window, RTT, sequence numbers, window sizes
- **tcp_retransmit_skb events**: Fired when TCP retransmits packets, capturing retransmission information

#### Generating Plots

Create visualizations from trace files:

```bash
# Generate plots from a trace file
tcp_probe plot trace.log

# Save plots to specific directory and open automatically
tcp_probe plot --output-dir ./plots --open trace.log

# Use raw timestamps instead of normalized time
tcp_probe plot --raw-time trace.log
```

Generated plots show:
1. **Congestion Window (snd_cwnd)** - TCP congestion control behavior
2. **Smoothed RTT (srtt)** - Round-trip time measurements  
3. **Retransmissions** - Timeline of packet retransmissions

### Python API

#### Parsing Trace Files

```python
import tcp_probe.parser as parser

# Parse a trace file
tcp_data, retrans_data = parser.parse_trace('trace.log')

# Parse individual lines
line = "tcp_probe: src=10.0.1.1:58760 dest=10.0.0.1:5201 ..."
parsed = parser.parse_tcp_probe_line(line)
print(parsed['snd_cwnd'])  # Access congestion window
```

#### Programmatic Plotting

```python
import tcp_probe.plot

# Generate plots programmatically
output_path = tcp_probe.plot.plot_trace(
    output_dir='./plots',
    trace_path='trace.log', 
    normalize_time=True
)
```

## Trace Data Format

### tcp_probe Events
Contains TCP connection state information:
- `timestamp`: When the event occurred
- `src`/`dest`: Source and destination IP:port
- `snd_cwnd`: Congestion window size
- `srtt`: Smoothed round-trip time
- `snd_nxt`/`snd_una`: Sequence number information
- `rcv_wnd`/`snd_wnd`: Receive/send window sizes
- `data_len`: Length of data in packet

### tcp_retransmit_skb Events  
Contains packet retransmission information:
- `timestamp`: When retransmission occurred
- `sport`/`dport`: Source and destination ports
- `saddr`/`daddr`: Source and destination IP addresses
- `state`: TCP connection state

## Requirements

- **Linux system** with kernel tracing support
- **Root privileges** for tracing (accesses `/sys/kernel/debug/tracing/`)
- **Python 3.x**

## Examples

### Monitor HTTP connections
```bash
# Trace HTTP traffic
sudo tcp_probe trace "sport == 80 || dport == 80 || sport == 443 || dport == 443" > http_trace.log

# Generate plots
tcp_probe plot http_trace.log
```

### Analyze specific connection
```bash
# Trace connections to specific IP
sudo tcp_probe trace "saddr == 192.168.1.100 || daddr == 192.168.1.100" > connection_trace.log

# Plot with custom output directory
tcp_probe plot --output-dir ./analysis connection_trace.log
```

### Long-running trace
```bash
# Large buffer for extended tracing
sudo tcp_probe trace --buffer 2000000 > long_trace.log &

# Stop with Ctrl+C when done
```

## File Format Support

- Plain text trace files
- Gzipped trace files (`.gz`)
- Supports both raw kernel timestamps and normalized time

## Additional Resources

- [TCP Tracepoints by Brendan Gregg](https://www.brendangregg.com/blog/2018-03-22/tcp-tracepoints.html) - Excellent deep dive into TCP tracepoints and their use cases
- [Linux kernel tcp_probe documentation](https://www.kernel.org/doc/html/latest/trace/events.html)
- [ftrace documentation](https://www.kernel.org/doc/html/latest/trace/ftrace.html) 
- [TCP tracing with ftrace](https://www.kernel.org/doc/html/latest/trace/events.html#event-filtering)

## Notes

- SSH connections (port 22) are automatically filtered out of plots to reduce noise
- Large traces benefit from increased buffer sizes (`--buffer` option) 
- The tool focuses on TCP behavior analysis and network performance debugging
- Requires `/sys/kernel/debug/tracing/` to be mounted (usually automatic on modern Linux)

## Contributing

Issues and pull requests welcome at https://github.com/brucespang/tcp_probe

