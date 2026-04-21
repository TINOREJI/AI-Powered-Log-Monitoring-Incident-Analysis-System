import pandas as pd
from src.preprocess.preprocess import preprocess_log
from src.classifier.classify import classify_log
from src.severity.severity import assign_severity
from src.aggregator.aggregator import aggregate

data = []
with open("src/dataset/log.csv", 'r') as f:
    next(f)  # skip header
    for line in f:
        timestamp, log_message = line.split(',', 1)
        data.append({'timestamp': timestamp, 'log_message': log_message.strip()})

df = pd.DataFrame(data)

results = []

for _, row in df.iterrows():
    p = preprocess_log(row)
    category = classify_log(p)
    severity = assign_severity(category)

    results.append({
        "timestamp": p["timestamp"],
        "ip": p["ip"],
        "category": category,
        "severity": severity,
        "log": p["raw"]
    })

output = aggregate(results)

print("\n--- SUMMARY ---")
print(output["category_summary"])

print("\n--- SEVERITY ---")
print(output["severity_summary"])

print("\n--- ALERTS ---")
for alert in output["alerts"]:
    print(alert)