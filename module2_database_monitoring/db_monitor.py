import mysql.connector
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os
import time

project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

def get_metric(cursor, metric_name, command_type="STATUS"):
    query = f"SHOW GLOBAL {command_type} LIKE %s"
    cursor.execute(query, (metric_name,))
    result = cursor.fetchone()
    return int(result[1]) if result else 0

try:
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = connection.cursor()
    print("MySQL connected successfully!")
    print("Monitoring started. Press Ctrl+C to stop.")

    while True:
        threads_connected = get_metric(cursor, "Threads_connected")
        threads_running = get_metric(cursor, "Threads_running")
        total_queries = get_metric(cursor, "Queries")
        slow_queries = get_metric(cursor, "Slow_queries")
        uptime = get_metric(cursor, "Uptime")
        max_connections = get_metric(cursor, "max_connections", "VARIABLES")

        query = """
        INSERT INTO Database_Metrics
        (timestamp, threads_connected, threads_running,
        total_queries, slow_queries, uptime, max_connections)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            datetime.now(),
            threads_connected,
            threads_running,
            total_queries,
            slow_queries,
            uptime,
            max_connections
        )

        cursor.execute(query, values)
        connection.commit()

        print(
            f"{datetime.now()} | "
            f"Connected: {threads_connected} | "
            f"Running: {threads_running} | "
            f"Queries: {total_queries} | "
            f"Slow: {slow_queries} | "
            f"Uptime: {uptime} | "
            f"Max Connections: {max_connections}"
        )

        time.sleep(10)

except KeyboardInterrupt:
    print("\nMonitoring stopped.")

except mysql.connector.Error as error:
    print("Database error:", error)

finally:
    if "connection" in locals() and connection.is_connected():
        if "cursor" in locals():
            cursor.close()
        connection.close()
        print("MySQL connection closed.")

