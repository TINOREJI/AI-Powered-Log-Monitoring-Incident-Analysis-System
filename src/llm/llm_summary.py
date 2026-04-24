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
You are an AI log monitoring assistant.

Analyze the system logs and return output STRICTLY in this format:

Summary:
- Max 5–10 bullet points
- Each point must be short (1 line)
- Describe overall system condition clearly

Critical Issues:
1. Most critical issue (include count if possible)
2. Second issue (include IP + time range if available)
3. Third issue (include system used percentage if applicable or any relevant metric)
4. Continue ONLY if important
5. Additional issue (if applicable)

Action Plan:
1. Most urgent action
2. Second action 
3. Third action
4. Continue in priority order
5. Additional action (if applicable)

STRICT RULES:
- NO paragraphs unless necessary for clarity
- NO explanations unless critical for understanding
- Keep everything concise
- ALWAYS prioritize by importance
- INCLUDE:
    • IP address (if suspicious activity exists)
    • Time range (if available in alerts)
    other relevant details (e.g., system usage, error counts)
- IGNORE "Other" category unless dominant
- Critical Issues must reflect real alerts or errors
- Actions must directly map to issues

Data:
Category Summary: {summary_data['category_summary']}
Severity Summary: {summary_data['severity_summary']}
Top Issues: {summary_data.get('top_issues', [])}
Alerts: {summary_data['alerts']}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
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
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    return response.text