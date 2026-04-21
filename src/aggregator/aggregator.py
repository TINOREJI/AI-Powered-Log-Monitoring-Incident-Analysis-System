from collections import Counter, defaultdict


# -------------------------
# Category Summary
# -------------------------
def get_category_summary(results):
    return dict(Counter([r["category"] for r in results]))


# -------------------------
# Severity Summary
# -------------------------
def get_severity_summary(results):
    return dict(Counter([r["severity"] for r in results]))


# -------------------------
# Detect repeated IP activity
# -------------------------
def detect_ip_patterns(results):
    ip_map = defaultdict(list)

    for r in results:
        if r["ip"]:
            ip_map[r["ip"]].append(r)

    alerts = []

    for ip, logs in ip_map.items():
        if len(logs) >= 3:
            categories = [l["category"] for l in logs]

            # 🔥 Filter weak categories
            filtered = [c for c in categories if c not in ["Other", "System Activity", "General Log"]]

            if filtered:
                most_common = Counter(filtered).most_common(1)[0][0]
            else:
                most_common = "General Activity"

            alerts.append({
                "type": "Security",
                "message": f"{len(logs)} suspicious activities ({most_common}) from IP {ip} between {logs[0]['timestamp']} and {logs[-1]['timestamp']}",
                "severity": "High"
            })

    return alerts


# -------------------------
# Detect repeated category spikes
# -------------------------
def detect_category_spikes(results):
    counts = Counter([r["category"] for r in results])
    alerts = []

    for cat, count in counts.items():
        if count >= 3 and cat in ["Security Alert", "Server Error", "System Error"]:
            alerts.append({
                "type": cat,
                "message": f"{count} {cat.lower()} events detected (possible issue requiring attention)",
                "severity": "High"
            })

    return alerts


# -------------------------
# Detect time-based spikes
# -------------------------
def detect_time_spikes(results):
    time_buckets = defaultdict(list)

    for r in results:
        key = r["timestamp"][:16]
        time_buckets[key].append(r)

    alerts = []

    for t, logs in time_buckets.items():
        if len(logs) >= 5:
            categories = Counter([l["category"] for l in logs])
            filtered = {k: v for k, v in categories.items() if k not in ["Other", "System Activity", "General Log"]}
            dominant = max(filtered, key=filtered.get) if filtered else "General Activity"

            alerts.append({
                "type": "Spike",
                "message": f"{len(logs)} logs at {t} (dominant: {dominant})",
                "severity": "Medium"
            })

    return alerts

def get_top_issues(results):
    counts = Counter([r["category"] for r in results])
    return counts.most_common(3)

# -------------------------
# Main Aggregator
# -------------------------
def aggregate(results):
    return {
        "category_summary": get_category_summary(results),
        "severity_summary": get_severity_summary(results),
        "top_issues": get_top_issues(results),
        "alerts": (
            detect_ip_patterns(results)
            + detect_category_spikes(results)
            + detect_time_spikes(results)
        )
    }