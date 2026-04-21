import pandas as pd
from ..preprocess.preprocess import preprocess_log

data = []
with open("src/dataset/log.csv", 'r') as f:
    next(f)  # skip header
    for line in f:
        timestamp, log_message = line.split(',', 1)
        data.append({'timestamp': timestamp, 'log_message': log_message.strip()})

df = pd.DataFrame(data)

sample = df.head(10)

for _, row in sample.iterrows():
    result = preprocess_log(row)
    print(result)