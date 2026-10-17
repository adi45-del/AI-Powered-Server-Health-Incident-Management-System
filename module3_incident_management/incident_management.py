
import os
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv


project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")


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
    INSERT INTO Incident (title, description, severity)
    VALUES (%s, %s, %s)
    """

    cursor.execute(query, (title, description, severity))
    connection.commit()
    print("Incident added successfully. ID:", cursor.lastrowid)
    cursor.close()


def get_incidents(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Incident ORDER BY incident_id DESC")
    incidents = cursor.fetchall()

    if not incidents:
        print("No incidents found.")
    else:
        for incident in incidents:
            print(incident)

    cursor.close()


def update_incident_status(connection, incident_id, status):
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE Incident SET status = %s WHERE incident_id = %s",
        (status, incident_id)
    )
    connection.commit()

    if cursor.rowcount:
        print("Incident status updated.")
    else:
        print("Incident ID not found.")

    cursor.close()


if __name__ == "__main__":
    connection = None

    try:
        connection = create_connection()
        print("MySQL connected successfully!")

        create_incident_table(connection)

        while True:
            print("\n--- Incident Management ---")
            print("1. Add test incident")
            print("2. View incidents")
            print("3. Resolve incident")
            print("4. Exit")

            choice = input("Enter choice: ")

            if choice == "1":
                add_incident(
                    connection,
                    "High CPU Usage",
                    "CPU usage exceeded the test threshold",
                    "Critical"
                )

            elif choice == "2":
                get_incidents(connection)

            elif choice == "3":
                try:
                    incident_id = int(input("Enter incident ID: "))
                    update_incident_status(
                        connection, incident_id, "RESOLVED"
                    )
                except ValueError:
                    print("Please enter a valid numeric ID.")

            elif choice == "4":
                print("Incident Management stopped.")
                break

            else:
                print("Invalid choice.")

    except mysql.connector.Error as error:
        print("MySQL error:", error)

    finally:
        if connection is not None and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")
