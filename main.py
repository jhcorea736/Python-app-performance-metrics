from ppadb.client import Client as AdbClient
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

def connect():
    # Default is "127.0.0.1" and 5037
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()

    if len(devices) == 0:
        print('No devices')
        quit()

    device = devices[0]
    print(f'Connected to {device}')
    return device, client

def get_app_pid(device, package_name):
    pid = device.shell(f'pidof -s {package_name}')
    return int(pid.strip()) if pid else None

def get_cpu_usage(device, pid):
    cpu_usage = device.shell(f'top -n 1 -d 1 -p {pid}').strip().split()[-4]
    return float(cpu_usage)

def get_memory_usage(device, pid):
    memory_usage = device.shell(f'dumpsys meminfo {pid}').strip().split('\n')
    for line in memory_usage:
        if 'TOTAL' in line:
            return int(line.split()[1])
        
def update_plot(frame):
    global cpu_data, memory_data, device, pid
    cpu_data.append(get_cpu_usage(device, pid))
    memory_data.append(get_memory_usage(device, pid))

    # Create the first subplot for CPU usage
    plt.subplot(2, 1, 1)  
    plt.plot(cpu_data, label='CPU Usage (%)', color='blue')
    plt.ylabel('CPU Usage (%)')
    plt.title('App CPU Usage')
    plt.grid(True)

    # Create the second subplot for memory usage
    plt.subplot(2, 1, 2)  
    plt.plot(memory_data, label='Memory Usage (KB)', color='green')
    plt.xlabel('Time (1 seconds interval)')
    plt.ylabel('Memory Usage (KB)')
    plt.title('App Memory Usage')
    plt.grid(True)
    
if __name__ == '__main__':
    # Set the package name of the app you want to measure performance
    package_name = "com.android.chrome"
    cpu_data, memory_data = [], []

    try:
        device, client = connect()
        pid = get_app_pid(device, package_name)

        if pid is None:
            print("App is not running on the device.")
        else:
            plt.figure(figsize=(10, 8))
            ani = FuncAnimation(plt.gcf(), update_plot, interval=1000)
            plt.tight_layout()
            plt.show()
            
    except KeyboardInterrupt:
        print("Measurement stopped by user.")