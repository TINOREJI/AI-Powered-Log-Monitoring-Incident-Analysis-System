import re
from datetime import datetime


# -------------------------
# Extract IP Address
# -------------------------
def extract_ip(log_message):
    match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', log_message)
    return match.group() if match else None


# -------------------------
# Extract HTTP Status Code
# -------------------------
def extract_status_code(log_message):
    match = re.search(r'\b(1\d{2}|2\d{2}|3\d{2}|4\d{2}|5\d{2})\b', log_message)
    return int(match.group()) if match else None


# -------------------------
# Extract basic log type (hint)
# -------------------------
def extract_log_hint(log_message):
    log = log_message.lower()

    # 🔐 SSH SECURITY (HIGHEST PRIORITY)
    if "sshd" in log:
        if any(x in log for x in [
            "failed password", "invalid user", "authentication failure"
        ]):
            return "security"

    # 🔐 GENERAL SECURITY
    if any(x in log for x in [
        "failed password", "invalid user", "authentication failure",
        "failed login", "unauthorized", "login failed", "access denied"
    ]):
        return "security"

    # 🌐 HTTP / API / nginx
    if any(x in log for x in [
        "get ", "post ", "http", "status", "request", "nginx"
    ]):
        return "http"

    # ❗ SYSTEM ERRORS
    if any(x in log for x in [
        "error", "failed", "timeout", "crash", "exception",
        "mysql", "database"
    ]):
        return "error"

    # 📈 RESOURCE
    if any(x in log for x in [
        "cpu", "memory", "disk", "usage", "load", "ram"
    ]):
        return "resource"

    # ⚙️ SYSTEM ACTIVITY
    if any(x in log for x in [
        "systemd", "kernel", "service", "daemon",
        "started", "starting", "stopped", "listening"
    ]):
        return "system"
    if any(x in log for x in [
    "started", "initialized", "loaded", "running"
    ]):
        return "system"

    return "other"
# -------------------------
# Main preprocessing function
# -------------------------
def preprocess_log(row):
    timestamp = row['timestamp']
    log_message = row['log_message']

    return {
        "timestamp": timestamp,
        "ip": extract_ip(log_message),
        "status_code": extract_status_code(log_message),
        "log_hint": extract_log_hint(log_message),
        "raw": log_message
    }