
from pathlib import Path
import os
import mysql.connector
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import IsolationForest

project_root = Path(__file__).resolve().parent
load_dotenv(project_root / ".env")


def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def test_normal_data():
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT cpu_usage, ram_usage, disk_usage
            FROM Server_Metrics
            WHERE cpu_usage IS NOT NULL
              AND ram_usage IS NOT NULL
              AND disk_usage IS NOT NULL
            ORDER BY `timestamp` ASC
        """)

        rows = cursor.fetchall()

        if len(rows) < 32:
            print("Need at least 32 records for testing.")
            return

        df = pd.DataFrame(
            rows,
            columns=["cpu_usage", "ram_usage", "disk_usage"]
        )

        features = df[["cpu_usage", "ram_usage", "disk_usage"]]
        split = int(len(features) * 0.8)

        training = features.iloc[:split]
        test_data = features.iloc[split:]

        model = IsolationForest(
            n_estimators=200,
            contamination=0.05,
            random_state=42
        )

        model.fit(training)
        predictions = model.predict(test_data)

        flagged = int((predictions == -1).sum())
        total = len(predictions)
        percentage = round(flagged / total * 100, 2)

        print("False-positive test completed.")
        print("Training records:", len(training))
        print("Test records:", total)
        print("Potential anomalies in test data:", flagged)
        print("Flagged percentage:", percentage, "%")

        print(
            "Note: These are flagged readings, not confirmed false positives. "
            "Ground-truth labels are required to calculate the actual "
            "false-positive rate."
        )

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    try:
        test_normal_data()
    except mysql.connector.Error as error:
        print("MySQL error:", error)
    except Exception as error:
        print("Error:", error)
