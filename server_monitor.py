import psutil
from datetime import datetime
import time

from database import create_connection, insert_metrics


connection = create_connection()
print("MySQL connected successfully!")


print("SERVER HEALTH MONITOR")
print("---------------------")


try:

    while True:

        
        cpu_usage = psutil.cpu_percent(interval=1)

    
        ram_usage = psutil.virtual_memory().percent

        
        disk_usage = psutil.disk_usage('/').percent

    
        disk_io = psutil.disk_io_counters()

        
        network = psutil.net_io_counters()

        
        running_processes = len(psutil.pids())

        
        current_time = datetime.now()


        
        if cpu_usage >= 90 or ram_usage >= 90 or disk_usage >= 90:
            health_status = "Critical"

        elif cpu_usage >= 75 or ram_usage >= 75 or disk_usage >= 75:
            health_status = "Warning"

        else:
            health_status = "Normal"


    
        print()
        print("Time:", current_time)
        print("CPU Usage:", cpu_usage, "%")
        print("RAM Usage:", ram_usage, "%")
        print("Disk Usage:", disk_usage, "%")
        print("Disk Read:", disk_io.read_bytes, "bytes")
        print("Disk Write:", disk_io.write_bytes, "bytes")
        print("Network Sent:", network.bytes_sent, "bytes")
        print("Network Received:", network.bytes_recv, "bytes")
        print("Running Processes:", running_processes)
        print("Health Status:", health_status)


        
        insert_metrics(
            connection,
            current_time,
            cpu_usage,
            ram_usage,
            disk_usage,
            disk_io.read_bytes,
            disk_io.write_bytes,
            network.bytes_sent,
            network.bytes_recv,
            running_processes
        )

        print("Data inserted into MySQL successfully!")

        
        print("Waiting for 10 seconds...")
        time.sleep(10)


except KeyboardInterrupt:

    print("\nMonitoring stopped by user.")


finally:

    connection.close()
    print("MySQL connection closed.")