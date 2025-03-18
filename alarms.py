import time
import config
import os
import subprocess
import psutil
if os.name == 'nt':
    from win10toast import ToastNotifier

def get_system_info():
    """Collects system metrics, including disk usage for all partitions."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_usages = []  # List to store disk usage for all partitions
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_name = partition.device.split('p')[0]  # Extract disk name (e.g., nvme0n1 from nvme0n1p1)

            disk_info = {
                'device': partition.device,
                'fstype': partition.fstype,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
            disk_usages.append(disk_info)
            if not any(disk['device'] == disk_name for disk in disks):
                disks.append({
                    'device': disk_name,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
        except (PermissionError, FileNotFoundError):
            print(f"Error accessing partition: {partition.device}")
            continue

    return cpu_usage, memory_info, disk_usages, disks

def trigger_alarm(metric, value):
    """Sends an email notification when a threshold is exceeded."""
    message = f"System Monitor Alert: {metric} exceeded threshold! Current value: {value}"
    send_alarm(message)

def send_alarm(message):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "favicon.png")
    if os.name == 'nt':
        toaster = ToastNotifier()
        toaster.show_toast("System Monitor Alert", message, icon_path=icon_path, duration=10)
    elif os.name == 'posix':
        if os.uname().sysname == 'Darwin':
            subprocess.run(['osascript', '-e', f'display notification "{message}" with title "System Monitor Alert"'])
        else:
            subprocess.run(['notify-send', 'System Monitor Alert', message, '--icon', icon_path])

def check_alarms():
    while True:
        global last_cpu_alert, last_memory_alert, last_disk_alert
        last_cpu_alert += 1
        last_memory_alert += 1
        last_disk_alert += 1
        print(last_cpu_alert, last_memory_alert)
        cpu_usage, memory_info, disk_usages, disks = get_system_info()
        if cpu_usage > config.cpu_threshold and last_cpu_alert > 20:
            trigger_alarm("CPU", cpu_usage)
            last_cpu_alert = 0
        if memory_info.percent > config.memory_threshold and last_memory_alert > 20:
            trigger_alarm("Memory", memory_info.percent)
            last_memory_alert = 0
        for disk_usage in disk_usages:
            if disk_usage['percent'] > config.disk_threshold and last_disk_alert > 600:
                trigger_alarm("Disk", f"{disk_usage['device']} ({disk_usage['percent']:.1f}%)")
        
        time.sleep(config.monitoring_interval)

def start_alarms():
    global last_cpu_alert, last_memory_alert, last_disk_alert
    last_cpu_alert = config.last_cpu_alert
    last_memory_alert = config.last_memory_alert
    last_disk_alert = config.last_disk_alert
    check_alarms()

def main():
    try:
        start_alarms()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()