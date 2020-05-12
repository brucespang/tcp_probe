import subprocess

def enable_event(event):
    f = open("/sys/kernel/debug/tracing/events/%s/enable"%event, mode='w')
    f.write('1')
    f.close()

def disable_event(event):
    f = open("/sys/kernel/debug/tracing/events/%s/enable"%event, mode='w')
    f.write('0')
    f.close()

def enable_tracing():
    f = open("/sys/kernel/debug/tracing/tracing_on", mode='w')
    f.write("1")
    f.close()

def disable_tracing():
    f = open("/sys/kernel/debug/tracing/tracing_on", mode='w')
    f.write("0")
    f.close()
    
def set_trace_buffer_size(buffer_size_kb):
    subprocess.check_call("echo %d > /sys/kernel/debug/tracing/buffer_size_kb"%buffer_size_kb,
                          shell=True)

def set_trace_filter(event, filter_string):
    f = open("/sys/kernel/debug/tracing/events/%s/filter"%event, mode='w')
    f.write(filter_string)
    f.close()
    
def clear_trace_buffer():
    subprocess.check_call('echo "" > /sys/kernel/debug/tracing/trace', shell=True)

def start_trace(output):
    return subprocess.Popen(['cat', '/sys/kernel/debug/tracing/trace_pipe'],
                            stdout=output)
