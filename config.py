# Configuration settings for the system monitor
cpu_threshold = 80  # CPU usage threshold (in percentage)
memory_threshold = 80  # Memory usage threshold (in percentage)
default_disk_threshold = 80  # Disk usage threshold (in percentage) default
monitoring_interval = 1  # Monitoring interval in seconds

disk_threshold = [{'device': '/dev/nvme0n1p3', 'threshold': 80}, {'device': '/dev/nvme0n1p2', 'threshold': 80}, {'device': '/dev/nvme0n1p1', 'threshold': 80}] # Disk thresholds for each partition

# Minimum time between alerts so the user isnt spammed
last_cpu_alert = 20
last_memory_alert = 20
last_disk_alert = 600
