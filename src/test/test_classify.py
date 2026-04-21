import pandas as pd
from src.preprocess.preprocess import preprocess_log
from src.classifier.classify import classify_log

data = []
with open("src/dataset/log.csv", 'r') as f:
    next(f)  # skip header
    for line in f:
        timestamp, log_message = line.split(',', 1)
        data.append({'timestamp': timestamp, 'log_message': log_message.strip()})

df = pd.DataFrame(data)

for _, row in df.head(10).iterrows():
    p = preprocess_log(row)
    category = classify_log(p)

    print(p["raw"])
    print("→", category)
    print("-" * 50)