import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def create_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def create_incident_table(connection):
    cursor = connection.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS Incident (
        incident_id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        severity VARCHAR(20),
        status VARCHAR(20) DEFAULT 'OPEN',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    cursor.execute(query)
    connection.commit()
    cursor.close()

    print("Incident table is ready.")


def add_incident(connection, title, description, severity):
    cursor = connection.cursor()

    query = """
    INSERT INTO Incident
    (title, description, severity)
    VALUES (%s, %s, %s)
    """

    cursor.execute(query, (title, description, severity))
    connection.commit()
    cursor.close()

    print("Incident added successfully.")


def get_incidents(connection):
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Incident")

    incidents = cursor.fetchall()

    for incident in incidents:
        print(incident)

    cursor.close()


def update_incident_status(connection, incident_id, status):
    cursor = connection.cursor()

    query = """
    UPDATE Incident
    SET status = %s
    WHERE incident_id = %s
    """

    cursor.execute(query, (status, incident_id))
    connection.commit()
    cursor.close()

    print("Incident status updated.")


if __name__ == "__main__":
    print("Incident Management Module")