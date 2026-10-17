import subprocess
import sys
import time

scripts = [
    "module1_server_monitoring/server_monitor.py",
    "module2_database_monitoring/db_monitor.py",
    "module3_incident_management/auto_detect.py"
]

processes = []

try:
   
    for script in scripts[:2]:
        print(f"Starting {script}")
        process = subprocess.Popen([sys.executable, script])
        processes.append(process)

    print("\nServer and database monitoring started.")
    print("Automatic incident detection will run every 30 seconds.")
    print("Press Ctrl+C to stop all monitoring.\n")

  
    while True:
        time.sleep(30)

        result = subprocess.run(
            [sys.executable, scripts[2]],
            check=False
        )

        if result.returncode != 0:
            print("Incident detection encountered an error.")

except KeyboardInterrupt:
    print("\nStopping monitoring...")

finally:
    for process in processes:
        process.terminate()

    for process in processes:
        process.wait()

    print("All monitoring processes stopped.")
