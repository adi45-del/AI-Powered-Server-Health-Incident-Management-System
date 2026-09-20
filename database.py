import mysql.connector


def create_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="server_health"
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