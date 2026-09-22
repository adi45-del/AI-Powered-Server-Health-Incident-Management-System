import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


def create_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    return connection


def insert_metrics(connection, current_time, cpu_usage, ram_usage, disk_usage,
                   disk_read, disk_write, network_sent, network_received,
                   running_processes):

    cursor = connection.cursor()

    query = """
    INSERT INTO Server_Metrics
    (timestamp, cpu_usage, ram_usage, disk_usage,
    disk_read, disk_write, network_sent, network_received,
    running_processes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        current_time,
        cpu_usage,
        ram_usage,
        disk_usage,
        disk_read,
        disk_write,
        network_sent,
        network_received,
        running_processes
    )

    cursor.execute(query, values)
    connection.commit()

    cursor.close()