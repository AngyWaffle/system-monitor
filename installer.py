import os
import utils
import utils.linux_utils
import utils.windows_utils
import platform

# Function to create a shortcut for the monitor.py
def create_shortcut():
    # Check the OS
    system = platform.system()

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

# Set the configuration values
def set_values():
    # Set the threshold values
    cpu_threshold = input("Enter the CPU threshold percentage (default 80): ")
    memory_threshold = input("Enter the memory threshold percentage (default 80): ")
    disk_threshold = input("Enter the disk threshold percentage (default 80): ")

    # Set the monitoring interval
    monitoring_interval = input("Enter the monitoring interval in seconds (default 1): ")

    # Set the minimum time between alerts
    cpu_interval = input("How often do you want to wait between CPU alerts in seconds (default 20): ")
    memory_interval = input("How often do you want to wait between memory alerts in seconds (default 20): ")
    disk_interval = input("How often do you want to wait between disk alerts in seconds (default 600): ")

    #Write the configuration values to the config.py file, with a default value if none is provided
    with open("config.py", "w") as f:
        f.write(f"""# Configuration settings for the system monitor
cpu_threshold = {cpu_threshold if cpu_threshold else 80}  # CPU usage threshold (in percentage)
memory_threshold = {memory_threshold if memory_threshold else 80}  # Memory usage threshold (in percentage)
disk_threshold = {disk_threshold if disk_threshold else 80}  # Disk usage threshold (in percentage)
monitoring_interval = {monitoring_interval if monitoring_interval else 1}  # Monitoring interval in seconds

# Minimum time between alerts so the user inst spammed
last_cpu_alert = {cpu_interval if cpu_interval else 20}
last_memory_alert = {memory_interval if memory_interval else 20}
last_disk_alert = {disk_interval if disk_interval else 600}
""")
    
    print("Configuration values set successfully!")

# Main function
if __name__ == "__main__":
    #Get the OS
    system = platform.system()

    # If the OS isnt windows or linux it hasnt been tested and therefore its unsuported
    if system != 'Windows' and system != 'Linux':
        print(f"Unsupported OS: {system}")
        SystemExit(1)
    
    # Check if the installer has ran before
    if is_first_run():
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
        mark_first_run()
        
        print("System Monitor installed successfully!")
        input("Press Enter to exit...")
    else: # If the installer has ran before
        print("System Monitor is already installed.") # Tell the user the installer has ran before
        change_values = input("Do you want to change the configuration values? (y/n): ") # Let them change the config values if they want to

        # If they want to change the values, let them
        if change_values.lower() == "y":
            set_values()
        
        input("Press Enter to exit...")