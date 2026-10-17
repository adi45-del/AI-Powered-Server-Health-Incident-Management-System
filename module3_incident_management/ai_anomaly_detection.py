import mysql.connector
import pandas as pd
from sklearn.ensemble import IsolationForest
from pathlib import Path
from dotenv import load_dotenv
import os


project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")


connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)


query = """
SELECT `timestamp`, cpu_usage, ram_usage, disk_usage
FROM Server_Metrics
WHERE cpu_usage IS NOT NULL
AND ram_usage IS NOT NULL
AND disk_usage IS NOT NULL
ORDER BY `timestamp` ASC
"""

df = pd.read_sql(query, connection)
connection.close()

print("Total historical records:", len(df))


if len(df) < 30:
    print("Not enough data. Collect at least 30 records first.")
    raise SystemExit


features = df[["cpu_usage", "ram_usage", "disk_usage"]]


model = IsolationForest(
    contamination="auto",
    random_state=42
)

df["prediction"] = model.fit_predict(features)


df["result"] = df["prediction"].map({
    -1: "Anomaly",
    1: "Normal"
})


print("\nAI Model Results:")
print(df["result"].value_counts())

print("\nRecent unusual readings:")
anomalies = df[df["result"] == "Anomaly"]

if anomalies.empty:
    print("No unusual readings detected.")
else:
    print(anomalies.tail(10).to_string(index=False))

print("\nAI anomaly detection completed.")