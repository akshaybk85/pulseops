import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

def ask_ai(alert_data):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are an expert DevOps/SRE engineer. Analyze this infrastructure alert and provide:
1. What is likely causing this issue
2. Immediate steps to fix it (be specific with commands)
3. How to prevent it in future

Alert Details:
{json.dumps(alert_data, indent=2)}

Keep response concise and actionable.
"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Groq API error: {response.text}"


def send_to_slack(message):
    if not SLACK_WEBHOOK_URL or SLACK_WEBHOOK_URL == "placeholder":
        print("Slack webhook not configured, skipping")
        return
    payload = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, json=payload)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "PulseOps AI Responder"})


@app.route("/alert", methods=["POST"])
def handle_alert():
    alert_data = request.json
    print(f"Received alert: {json.dumps(alert_data, indent=2)}")

    diagnosis = ask_ai(alert_data)
    print(f"AI Diagnosis: {diagnosis}")

    alerts = alert_data.get("alerts", [{}])
    alert_name = alerts[0].get("labels", {}).get("alertname", "Unknown Alert")
    severity = alerts[0].get("labels", {}).get("severity", "unknown")

    slack_message = f"""
🚨 *PulseOps Alert: {alert_name}*
Severity: `{severity}`

🤖 *AI Diagnosis:*
{diagnosis}
"""

    send_to_slack(slack_message)

    return jsonify({
        "status": "processed",
        "alert": alert_name,
        "diagnosis": diagnosis
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)