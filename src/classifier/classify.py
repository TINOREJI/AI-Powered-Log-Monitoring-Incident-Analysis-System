# -------------------------
# Map HTTP status → category
# -------------------------
def classify_http(status_code):
    if status_code is None:
        return None

    if 200 <= status_code < 300:
        return "Info"
    elif 300 <= status_code < 400:
        return "Redirect"
    elif 400 <= status_code < 500:
        return "Client Error"
    elif 500 <= status_code < 600:
        return "Server Error"

    return "Other"


# -------------------------
# Main classification logic
# -------------------------
def classify_log(preprocessed):
    hint = preprocessed["log_hint"]
    status_code = preprocessed["status_code"]

    # 1. HTTP-based classification
    http_category = classify_http(status_code)
    if http_category:
        return http_category

    # 2. Rule-based classification
    if hint == "security":
        return "Security Alert"

    elif hint == "error":
        return "System Error"

    elif hint == "resource":
        return "Resource Usage"

    elif hint == "http":
        return "HTTP Activity"
    
    elif hint == "system":
        return "System Activity"

    return "Other"