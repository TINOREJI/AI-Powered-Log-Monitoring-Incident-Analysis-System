SEVERITY_MAP = {
    "Security Alert": "High",
    "Server Error": "Critical",
    "Client Error": "Medium",
    "System Error": "High",
    "Resource Usage": "Medium",
    "HTTP Activity": "Low",
    "Info": "Low",
    "Redirect": "Low",
    "Other": "Low",
    "System Activity": "Low",
}


def assign_severity(category: str, log: str = ""):
    log_lower = log.lower()

    # 🔥 Dynamic overrides

    # Security escalation
    if category == "Security Alert":
        if any(x in log_lower for x in ["failed password", "unauthorized", "invalid user"]):
            return "Critical"

    # System error escalation
    if category in ["System Error", "Server Error"]:
        if "timeout" in log_lower or "crash" in log_lower:
            return "Critical"

    # Resource escalation
    if category == "Resource Usage":
        if any(x in log_lower for x in ["95%", "98%", "99%"]):
            return "High"

    # Default mapping
    return SEVERITY_MAP.get(category, "Low")