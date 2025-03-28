import time
from psutil._common import bytes2human
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from alarms import get_system_info

# Declare root globaly
global root
root = tk.Tk()

# Close window
def on_closing():
    root.destroy()

# Build the gui
def start_gui():
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.title("System Monitor")

    # Data storage for graph
    root.cpu_data = []
    root.ram_data = []
    root.time_data = []

    # Create frame structure
    root.left_frame = ttk.Frame(root)
    root.left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
    root.right_frame = ttk.Frame(root)
    root.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

    # Create graph frame
    root.graph_frame = ttk.Frame(root.left_frame)
    root.graph_frame.pack(fill=tk.BOTH, expand=True)

    # Create graph
    root.fig, root.ax = plt.subplots()
    root.canvas = FigureCanvasTkAgg(root.fig, master=root.graph_frame)
    root.canvas_widget = root.canvas.get_tk_widget()
    root.canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create labels
    root.system_label = ttk.Label(root.right_frame, text="System Information:", font=("Helvetica", 14, "bold"))
    root.system_label.pack(anchor=tk.W)

    root.cpu_label = ttk.Label(root.right_frame, text="", font=("Helvetica", 12))
    root.cpu_label.pack(anchor=tk.W)

    root.memory_label = ttk.Label(root.right_frame, text="", font=("Helvetica", 12))
    root.memory_label.pack(anchor=tk.W)

    root.disk_label = ttk.Label(root.right_frame, text="Disk Information:", font=("Helvetica", 14, "bold"))
    root.disk_label.pack(anchor=tk.W)

    # Create disk frame
    root.disk_info_frame = ttk.Frame(root.right_frame)
    root.disk_info_frame.pack(fill=tk.BOTH, expand=True)

    # Make the disk frame scrollable
    root.canvas_disk = tk.Canvas(root.disk_info_frame)
    root.scrollbar = ttk.Scrollbar(root.disk_info_frame, orient="vertical", command=root.canvas_disk.yview)
    root.scrollable_frame = ttk.Frame(root.canvas_disk)

    root.scrollable_frame.bind(
        "<Configure>",
        lambda e: root.canvas_disk.configure(
            scrollregion=root.canvas_disk.bbox("all")
        )
    )

    root.canvas_disk.create_window((0, 0), window=root.scrollable_frame, anchor="nw")
    root.canvas_disk.configure(yscrollcommand=root.scrollbar.set, highlightthickness=2, highlightbackground="black")

    root.canvas_disk.pack(side="left", fill="both", expand=True)
    root.scrollbar.pack(side="right", fill="y")

    root.disk_info_label = ttk.Label(root.scrollable_frame, text="", font=("Helvetica", 12), justify="left")
    root.disk_info_label.pack(anchor=tk.W)

    root.geometry("1920x1080")

    update_info() #Start update loop
    root.mainloop()

# Update the system info
def update_info():
    # Get current usage
    cpu_usage, memory_info, disk_usages = get_system_info()

    # Update the labels
    root.cpu_label.config(text=f"\nCPU Usage: {cpu_usage}%")
    root.memory_label.config(text=f"Memory used: {memory_info.percent}% \n"
                        f"Memory available: {bytes2human(memory_info.available)}B of {bytes2human(memory_info.total)}B\n")

    disk_info_text = ""
    for disk_usage in disk_usages:
        disk_info_text += (f"  \nDevice: {disk_usage['device']}\n"
                        f"  Total: {bytes2human(disk_usage['total'])}B\n"
                        f"  Used: {bytes2human(disk_usage['used'])}B\n"
                        f"  Free: {bytes2human(disk_usage['free'])}B\n"
                        f"  Disk Used: {disk_usage['percent']}%\n"
                        f"  \n")

    root.disk_info_label.config(text=disk_info_text)

    root.cpu_data.append(cpu_usage)
    root.ram_data.append(memory_info.percent)
    root.time_data.append(time.time())

    # Make the graph contain max 300 entries (About 2.5-5 minutes)
    if len(root.cpu_data) > 300:
        root.cpu_data.pop(0)
        root.ram_data.pop(0)
        root.time_data.pop(0)

    # Update the graph
    root.ax.clear()
    root.ax.plot(root.time_data, root.cpu_data, label='CPU Usage (%)', color='blue')
    root.ax.plot(root.time_data, root.ram_data, label='RAM Usage (%)', color='green')
    root.ax.set_title('CPU and RAM Usage Over the Last 5 Minutes')
    root.ax.set_ylabel('Usage (%)')
    root.ax.legend(fontsize=14)
    root.ax.grid()
    root.ax.set_ylim(0, 100)
    root.ax.set_xticks([])

    root.canvas.draw()

    # Loop every 0.5 seconds
    root.after(500, lambda:update_info())

# Main function
if __name__ == "__main__":
    start_gui()