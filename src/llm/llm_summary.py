import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = None
LLM_AVAILABLE = False

try:
    if API_KEY:
        client = genai.Client(api_key=API_KEY)
        LLM_AVAILABLE = True
except Exception as e:
    print(f"LLM Init Error: {e}")


def generate_summary(summary_data):
    if not LLM_AVAILABLE:
        return "LLM not available"

    prompt = f"""
Summarize the system logs:

Category Summary: {summary_data['category_summary']}
Severity Summary: {summary_data['severity_summary']}
Top Issues: {summary_data.get('top_issues', [])}
Alerts: {summary_data['alerts']}

Give:
1. System condition
2. Critical issues
3. Suggested actions
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def ask_llm(question, summary_data):
    if not LLM_AVAILABLE:
        return "LLM not available"

    prompt = f"""
You are an AI log monitoring assistant.

System Data:
Category Summary: {summary_data['category_summary']}
Severity Summary: {summary_data['severity_summary']}
Top Issues: {summary_data.get('top_issues', [])}
Alerts: {summary_data['alerts']}

User Question:
{question}

Answer clearly.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text