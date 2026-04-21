from src.pipeline.pipeline import process_logs

output = process_logs("src/dataset/log.csv")

print("\n=== CATEGORY SUMMARY ===")
print(output["summary"]["category_summary"])

print("\n=== SEVERITY SUMMARY ===")
print(output["summary"]["severity_summary"])

print("\n=== ALERTS ===")
for alert in output["summary"]["alerts"]:
    print(alert)

# print("\n=== SAMPLE LOG OUTPUT ===")
# for log in output["processed_logs"][:5]:
#     print(log)
print("\n=== AI SUMMARY ===")
print(output["llm_summary"])