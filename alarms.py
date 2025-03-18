import time
import config
import os
import subprocess
import psutil
import platform
# Library unavaiable on Linux so only import on Windows
if os.name == 'nt':
    from win10toast import ToastNotifier

# Get the current system usage
def get_system_info():
    # Get CPU, memory and disk usage
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()

    disk_usages = []  # List to store disk usage for all partitions 
    for partition in psutil.disk_partitions(): # Loop through all partitions
        try:
            usage = psutil.disk_usage(partition.mountpoint) # Get usage

            # Store the disk info in a dictionary
            disk_info = {
                'device': partition.device,
                'fstype': partition.fstype,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
            # If the disk is dupe, skip it
            if disk_info in disk_usages:
                continue
            else:
                disk_usages.append(disk_info) # Add disk to array
        except (PermissionError, FileNotFoundError): # Handle errors
            print(f"Error accessing partition: {partition.device}")
            continue

    return cpu_usage, memory_info, disk_usages # Return the values

# Trigger an alarm
def trigger_alarm(metric, value):
    # Create the alarm message
    message = f"System Monitor Alert: {metric} exceeded threshold! Current value: {value}"

    send_alarm(message) # Send the alarm

# Send the alarm
def send_alarm(message):
    # Get OS
    system = platform.system()

    # Get the path to the icon
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "favicon.png")

    # Check the OS
    if system == 'Windows':
        # Use ToastNotifier for windows
        toaster = ToastNotifier()
        toaster.show_toast("System Monitor Alert", message, icon_path=icon_path, duration=10)
    elif system == 'Linux':
        # Use notify-send for Linux
        subprocess.run(['notify-send', 'System Monitor Alert', message, '--icon', icon_path])

# Check if alarms should be triggered
def check_alarms():
    # Loop forever
    while True:
        # Update the time since last alert
        global last_cpu_alert, last_memory_alert, last_disk_alerts
        last_cpu_alert += 1
        last_memory_alert += 1
        for disk in last_disk_alerts:
            last_disk_alerts[disk] += 1
        
        # Get the current system usage
        cpu_usage, memory_info, disk_usages = get_system_info()

        # Update the devices that might have been removed
        current_devices = {disk['device'] for disk in disk_usages}
        last_disk_alerts = {device: alert_time for device, alert_time in last_disk_alerts.items() if device in current_devices}

        # Add new devices to the disk alert list
        for disk_usage in disk_usages:
            device = disk_usage['device']
            if device not in last_disk_alerts:
                last_disk_alerts[device] = config.last_disk_alert

        # Check if CPU usage is above the threshold
        if cpu_usage > config.cpu_threshold and last_cpu_alert > config.last_cpu_alert:
            trigger_alarm("CPU", cpu_usage)
            last_cpu_alert = 0 # Reset the time since last alert

        # Check if the memory usage is above the threshold
        if memory_info.percent > config.memory_threshold and last_memory_alert > config.last_memory_alert:
            trigger_alarm("Memory", memory_info.percent) 
            last_memory_alert = 0

        # Check each disk if the uage is above the threshold
        for disk_usage in disk_usages:
            # Get the disk
            device = disk_usage['device']
            # Check if the disk usage is above the threshold
            if disk_usage['percent'] > config.disk_threshold and last_disk_alerts[device] > config.last_disk_alert:
                trigger_alarm("Disk", f"{disk_usage['device']} ({disk_usage['percent']:.1f}%)")
                last_disk_alerts[device] = 0 # Reset that disks time since last alert
        
        # Wait for the monitoring interval
        time.sleep(config.monitoring_interval)

# Start the alarms
def start_alarms():
    # Declare the variables for alarm cooldown as global
    global last_cpu_alert, last_memory_alert, last_disk_alerts
    last_cpu_alert = config.last_cpu_alert
    last_memory_alert = config.last_memory_alert
    last_disk_alerts = {}

    # Start the monitoring
    check_alarms()

# Main function
def main():
    # Start the alarms
    try:
        start_alarms()
    except Exception as e:
        print(f"An error occurred: {e}")

# Start the script
if __name__ == "__main__":
    # Get the os
    system = platform.system()

    # Kill the script if not Windows or Linux
    if system != 'Windows' and system != 'Linux':
        print(f"Unsupported OS: {system}")
        SystemExit(1)
    
    # Start the script
    main()