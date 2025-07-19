import time
import psutil
import os
import platform

# Cache system stats and update every 3 seconds to reduce overhead
last_update_time = 0
cached_temp, cached_cpu, cached_memory = None, None, None

def get_system_stats():
    """Fetch system stats only if at least 3 seconds have passed. Never crash if a value can't be obtained."""
    global last_update_time, cached_temp, cached_cpu, cached_memory
    now = time.time()

    if now - last_update_time >= 3:  # Limit updates to once every 3 seconds to reduce overhead
        last_update_time = now

        # Detect OS
        is_windows = platform.system() == "Windows"
        is_linux = platform.system() == "Linux"

        # Get CPU usage (non-blocking)
        try:
            cached_cpu = psutil.cpu_percent(interval=0)
        except Exception:
            cached_cpu = None

        # Get memory usage
        try:
            cached_memory = psutil.virtual_memory().percent
        except Exception:
            cached_memory = None

        # Get CPU temperature
        cached_temp = None
        if is_linux:
            try:
                cached_temp = float(os.popen("vcgencmd measure_temp").readline().replace("temp=", "").replace("'C\n", ""))
            except Exception:
                try:
                    temps = psutil.sensors_temperatures()
                    if "coretemp" in temps:
                        cached_temp = temps["coretemp"][0].current
                except Exception:
                    cached_temp = None
        elif is_windows:
            try:
                temps = psutil.sensors_temperatures()
                if "cpu_thermal" in temps:
                    cached_temp = temps["cpu_thermal"][0].current
            except Exception:
                cached_temp = None

    return cached_temp, cached_cpu, cached_memory