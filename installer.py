import os
import utils
import utils.linux_utils
if os.name == 'nt':
    import utils.windows_utils
import platform
import subprocess
import sys
from alarms import get_system_info

# Function to create a shortcut for the monitor.py
def create_shortcut():
    #Check if user wants the monitor script
    shortcut = input("Do you want to install a custom, real time system monitor? (y/n): ")

    # If user wants the monitor script, create the shortcut
    if shortcut.lower() == "y": 
        if system == "Windows": # Windows
            utils.windows_utils.create_windows_shortcut() # Create the windows shortcut
        elif system == "Linux": # Linux
            utils.linux_utils.create_linux_shortcut() # Create the linux shortcut

# Function to check if the installer has ran before
def is_first_run():
    # Check if the first_run.txt file exists
    return not os.path.exists("first_run.txt")

# Function to mark the first run
def mark_first_run():
    # Create the first_run.txt file
    with open("first_run.txt", "w") as f:
        f.write("This file indicates the script has run before.")

# Function to install the required packages
def install_packages():
    # List of required packages
    packages = [
        "matplotlib",
        "psutil",
        "tkinter"
    ]
    
    # Add win10toast if OS is windows
    if system == "Windows":
        packages.append("win10toast")
        packages.append("winshell")
    
    try:
        # Install the packages
        for package in packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError as e:
        print(f"Error installing package: {e}")

# Set the configuration values
def set_values():
    # Set the threshold values
    cpu_threshold = input("Enter the CPU threshold percentage (default 80): ")
    memory_threshold = input("Enter the memory threshold percentage (default 80): ")

    disk_threshold = []

    _, _, disk_usages = get_system_info()
    disk_names = []
    for disk in disk_usages:
        device = disk['device']
        if device not in disk_names:
            disk_names.append(device)
    
    print(f"Available disks: {', '.join(disk_names)}")
    
    for disk in disk_usages:
        print(f"Device: {disk['device']}")
        
        device_threshold = input(f"Enter the disk threshold for {disk['device']} in percentage (default 80): ")
        partition_threshold = {'device': disk['device'], 'threshold': device_threshold if device_threshold else 80}
        disk_threshold.append(partition_threshold)

    # Set the default disk threshold
    default_disk_threshold = input("Enter the default disk threshold in percentage (default 80): ")

    # Set the monitoring interval
    monitoring_interval = input("Enter the monitoring interval in seconds (default 1): ")

    # Set the minimum time between alerts
    cpu_interval = input("How often do you want to wait between CPU alerts in monitoring intervals (default 20): ")
    memory_interval = input("How often do you want to wait between memory alerts in monitoring intervals (default 20): ")
    disk_interval = input("How often do you want to wait between disk alerts in monitoring intervals (default 600): ")

    #Write the configuration values to the config.py file, with a default value if none is provided
    with open("config.py", "w") as f:
        f.write(f"""# Configuration settings for the system monitor
cpu_threshold = {cpu_threshold if cpu_threshold else 80}  # CPU usage threshold (in percentage)
memory_threshold = {memory_threshold if memory_threshold else 80}  # Memory usage threshold (in percentage)
default_disk_threshold = {default_disk_threshold if default_disk_threshold else 80}  # Disk usage threshold (in percentage) default
monitoring_interval = {monitoring_interval if monitoring_interval else 1}  # Monitoring interval in seconds

disk_threshold = {disk_threshold} # Disk thresholds for each partition

# Minimum time between alerts so the user isnt spammed
last_cpu_alert = {cpu_interval if cpu_interval else 20}
last_memory_alert = {memory_interval if memory_interval else 20}
last_disk_alert = {disk_interval if disk_interval else 600}
""")
    
    print("Configuration values set successfully!")

# Main function
if __name__ == "__main__":
    #Get the OS
    global system
    system = platform.system()

    # If the OS isnt windows or linux it hasnt been tested and therefore its unsuported
    if system != 'Windows' and system != 'Linux':
        print(f"Unsupported OS: {system}")
        SystemExit(1)
    
    # Check if the installer has ran before
    if is_first_run():
        # Install the required packages
        install_packages()

        # Create the shortcut
        create_shortcut()

        # Set the config values
        set_values()

        # Add monitor alerts to the system to start on boot
        if system == 'Windows':  # Windows
            utils.windows_utils.add_to_startup_windows()
        elif system == 'Linux':  # Linux
                utils.linux_utils.add_to_startup_linux()

        # Mark the first run
        #mark_first_run()
        
        print("System Monitor installed successfully!")
        mark_first_run()
        input("Press Enter to exit...")
    else: # If the installer has ran before
        print("System Monitor is already installed.") # Tell the user the installer has ran before
        change_values = input("Do you want to change the configuration values? (y/n): ") # Ask them if they want to change the config values

        # If they want to change the values, let them
        if change_values.lower() == "y":
            set_values()
            if system == 'Windows':  # Windows
                utils.windows_utils.add_to_startup_windows()
            elif system == 'Linux':  # Linux
                utils.linux_utils.restart_service()
        
        input("Press Enter to exit...")