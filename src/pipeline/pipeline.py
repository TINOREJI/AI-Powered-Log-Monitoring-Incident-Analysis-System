import pandas as pd

from src.preprocess.preprocess import preprocess_log
from src.classifier.classify import classify_log
from src.severity.severity import assign_severity
from src.aggregator.aggregator import aggregate
from src.ml.ml_classifier import ml_classify
from src.llm.llm_summary import generate_summary


def process_logs(file_path: str):
    data = []

    # -------------------------
    # Safe file reading
    # -------------------------
    with open(file_path, 'r') as f:
        next(f)  # skip header

        for line in f:
            parts = line.strip().split(',', 1)

            if len(parts) < 2:
                continue

            timestamp, log_message = parts
            data.append({
                'timestamp': timestamp,
                'log_message': log_message.strip()
            })

    df = pd.DataFrame(data)

    results = []

    # -------------------------
    # Main pipeline
    # -------------------------
    for _, row in df.iterrows():
        p = preprocess_log(row)

        # Step 1: Rule-based classification
        category = classify_log(p)

        # Step 2: ML fallback (only if needed)
        category = ml_classify(p["raw"], category)

        # Step 3: Assign severity AFTER final category
        severity = assign_severity(category)

        results.append({
            "timestamp": p["timestamp"],
            "ip": p["ip"],
            "category": category,
            "severity": severity,
            "log": p["raw"]
        })

    # -------------------------
    # Aggregation
    # -------------------------
    summary = aggregate(results)

    # -------------------------
    # LLM Summary (final layer)
    # -------------------------
    try:
        llm_output = generate_summary(summary)
    except Exception as e:
        llm_output = f"LLM summary failed: {e}"

    return {
        "processed_logs": results,
        "summary": summary,
        "llm_summary": llm_output
    }