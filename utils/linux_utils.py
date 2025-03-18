# Description: This file contains the functions nessesary to create a linux shortcut and to add the monitor-alerts service to the system for real time monitoring and automatic startup.
import os
import subprocess

# Add the monitor-alerts as a service to the system
def add_to_startup_linux():
    # Get the path to alarms.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    alarms_path = os.path.join(parent_dir, "alarms.py")
    
    # Create the service file
    service_content = f"""[Unit]
    Description=A simple Python script to monitor system resources
    After=network.target
    StartLimitIntervalSec=0

    [Service]
    Name=monitor-alerts.service
    User={os.getlogin()}
    Type=simple
    ExecStart=/usr/bin/python3 {alarms_path}
    Restart=always
    RestartSec=20
    Environment=DISPLAY=:0
    Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus

    [Install]
    WantedBy=multi-user.target
    """

    # Set the path for the service
    service_path = "/etc/systemd/system/monitor-alerts.service"
    # Write the service file
    with open(service_path, "w") as service_file:
        service_file.write(service_content)

    # Add the service to the system
    try:
        os.system("sudo systemctl daemon-reload")
        os.system("sudo systemctl enable monitor-alerts.service")
        os.system("sudo systemctl start monitor-alerts.service")
        print("Service added successfully!")
    except Exception as e:
        print(f"Error with service: {e}")

# Create a shortcut to the monitor
def create_linux_shortcut():
    # Get the path where the shortcut will be created
    user_home = os.path.expanduser("~" + os.getenv("SUDO_USER", ""))
    desktop_entry_path = os.path.join(user_home, ".local/share/applications/monitor.desktop")
    
    # Get the path to the monitor.py and the icon
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    monitor_path = os.path.join(parent_dir, "monitor.py")
    icon_path = os.path.join(parent_dir, "favicon.png")

    # Make monitor.py executable
    try:
        os.chmod(monitor_path, 0o755)
    except Exception as e:
        print(f"Error setting permissions for monitor.py: {e}")

    # Create the desktop entry file
    desktop_entry_content = f"""[Desktop Entry]
Version=1.0
Name=Python System Monitor
Comment=Monitor system resources
Exec=env QT_QPA_PLATFORM=wayland /usr/bin/python3 {monitor_path}
Icon={icon_path}
Terminal=true
Type=Application
Categories=Utility;System;
"""
    # Create the desktop entry file
    try:
        # Create the path for the desktop entry
        os.makedirs(os.path.dirname(desktop_entry_path), exist_ok=True)
        # Write the desktop entry file
        with open(desktop_entry_path, "w") as desktop_file:
            desktop_file.write(desktop_entry_content)
        # Make the desktop entry file executable
        os.chmod(desktop_entry_path, 0o755)

        # Update the desktop database
        subprocess.run(["update-desktop-database", os.path.dirname(desktop_entry_path)], check=True)
        print("Linux shortcut created successfully!")
    except Exception as e:
        print(f"Error creating shortcut: {e}")
