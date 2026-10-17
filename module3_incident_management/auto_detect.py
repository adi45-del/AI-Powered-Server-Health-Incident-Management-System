
from pathlib import Path
import os
import mysql.connector
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import IsolationForest

project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")


def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def create_incident(cursor, title, description, severity="Warning"):
    cursor.execute(
        """
        SELECT incident_id
        FROM Incident
        WHERE title = %s AND status = 'OPEN'
        LIMIT 1
        """,
        (title,)
    )

    if cursor.fetchone():
        print("Already open:", title)
        return

    cursor.execute(
        """
        INSERT INTO Incident (title, description, severity, status)
        VALUES (%s, %s, %s, 'OPEN')
        """,
        (title, description, severity)
    )

    print("Incident created:", title)


def run_ai_detection(cursor, df, feature_columns, title, metric_name):
    features = df[feature_columns].apply(
        pd.to_numeric, errors="coerce"
    )

    valid = features.notna().all(axis=1)
    df = df.loc[valid].reset_index(drop=True)
    features = features.loc[valid].reset_index(drop=True)

    print(f"{metric_name} valid records:", len(features))

    if len(features) < 32:
        print(f"{metric_name}: Need at least 32 valid records.")
        return

    training_features = features.iloc[:-2]
    latest_features = features.iloc[-2:]

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42
    )

    model.fit(training_features)

    historical_predictions = model.predict(training_features)
    latest_predictions = model.predict(latest_features)

    anomaly_count = int((historical_predictions == -1).sum())
    anomaly_percentage = round(
        anomaly_count / len(historical_predictions) * 100, 2
    )

    print(f"{metric_name} historical potential anomalies:", anomaly_count)
    print(f"{metric_name} historical anomaly percentage:",
          anomaly_percentage, "%")
    print(f"{metric_name} latest two predictions:",
          latest_predictions.tolist())

    latest = df.iloc[-1]

    details = ", ".join(
        f"{column}={latest[column]}" for column in feature_columns
    )

    if all(prediction == -1 for prediction in latest_predictions):
        print(f"{metric_name}: Anomaly confirmed in two consecutive readings.")

        create_incident(
            cursor,
            title,
            f"Isolation Forest detected unusual {metric_name} metrics "
            f"in two consecutive readings. Latest values: {details}. "
            "Manual verification is recommended.",
            "Warning"
        )

    elif any(prediction == -1 for prediction in latest_predictions):
        print(
            f"{metric_name}: Potential anomaly detected. "
            "Waiting for further confirmation."
        )

    else:
        print(f"{metric_name}: Latest two readings classified as Normal.")


def detect_server_issues(cursor):
    cursor.execute("""
        SELECT `timestamp`, cpu_usage, ram_usage, disk_usage
        FROM Server_Metrics
        WHERE cpu_usage IS NOT NULL
        AND ram_usage IS NOT NULL
        AND disk_usage IS NOT NULL
        ORDER BY `timestamp` ASC
    """)

    rows = cursor.fetchall()

    df = pd.DataFrame(
        rows,
        columns=["timestamp", "cpu_usage", "ram_usage", "disk_usage"]
    )

    print("Server historical records:", len(df))

    run_ai_detection(
        cursor,
        df,
        ["cpu_usage", "ram_usage", "disk_usage"],
        "AI Detected Server Anomaly",
        "Server"
    )


def detect_database_issues(cursor):
    cursor.execute("""
        SELECT `timestamp`, threads_connected, threads_running,
               total_queries, slow_queries, max_connections
        FROM Database_Metrics
        ORDER BY `timestamp` ASC
    """)

    rows = cursor.fetchall()

    df = pd.DataFrame(
        rows,
        columns=[
            "timestamp",
            "threads_connected",
            "threads_running",
            "total_queries",
            "slow_queries",
            "max_connections"
        ]
    )

    print("Database historical records:", len(df))

    if df.empty:
        print("No database metrics found.")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["elapsed_seconds"] = (
        df["timestamp"].diff().dt.total_seconds()
    )

    df["query_rate"] = (
        df["total_queries"].diff() / df["elapsed_seconds"]
    )

    df["slow_query_rate"] = (
        df["slow_queries"].diff() / df["elapsed_seconds"]
    )

    df["connection_utilization"] = (
        df["threads_connected"] /
        df["max_connections"].where(df["max_connections"] > 0)
    )

    df["query_rate"] = df["query_rate"].where(
        (df["query_rate"] >= 0) & (df["elapsed_seconds"] > 0)
    )

    df["slow_query_rate"] = df["slow_query_rate"].where(
        (df["slow_query_rate"] >= 0) & (df["elapsed_seconds"] > 0)
    )

    feature_columns = [
        "threads_connected",
        "threads_running",
        "connection_utilization",
        "query_rate",
        "slow_query_rate"
    ]

    run_ai_detection(
        cursor,
        df,
        feature_columns,
        "AI Detected Database Anomaly",
        "Database"
    )


def main():
    connection = None
    cursor = None

    try:
        connection = connect_db()
        cursor = connection.cursor()

        print("MySQL connected successfully.")

        detect_server_issues(cursor)
        detect_database_issues(cursor)

        connection.commit()
        print("Automatic incident check completed.")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    try:
        main()
    except mysql.connector.Error as error:
        print("MySQL error:", error)
    except Exception as error:
        print("Error:", error)
