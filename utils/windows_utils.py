import os
import shutil
import winshell
from win32com.client import Dispatch

def add_to_startup_windows():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    alarms_path = os.path.join(parent_dir, "alarms.py")
    bat_file_path = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\monitor-alerts.bat")
    with open(bat_file_path, "w") as bat_file:
        bat_file.write(f'@echo off\npython "{alarms_path}"\n')

def create_windows_shortcut():
    # Get the path where the shortcut will be created
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    monitor_path = os.path.join(parent_dir, "monitor.py")
    shortcut_path = os.path.join(winshell.start_menu(), "System Monitor.lnk")
    icon_path = os.path.join(parent_dir, "favicon.ico")

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = f"python {monitor_path}"
    shortcut.WorkingDirectory = script_dir
    shortcut.IconLocation = icon_path
    shortcut.save()

    print("Windows shortcut created successfully!")