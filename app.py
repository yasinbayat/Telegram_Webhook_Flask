import os
import json
from flask import Flask, request, jsonify
import requests
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

# Telegram config
TELEGRAM_BOT_TOKEN = "8192934063:AAHkpQ2rBk_WQkHdXJcdYy2kXBIqlYvZGcQ"
TELEGRAM_CHAT_ID = "269768639"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# Ensure alert directory exists
ALERT_DIR = "alerts"
os.makedirs(ALERT_DIR, exist_ok=True)

# Helper: Send message to Telegram
def send_telegram_message(message):
    try:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(TELEGRAM_API_URL, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Telegram send error: {e}")

# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        alerts = data.get("alerts", [])

        if not alerts:
            return jsonify({"error": "No alerts found"}), 400

        for alert in alerts:
            try:
                labels = alert.get("labels", {})
                annotations = alert.get("annotations", {})

                team = labels.get("team")
                severity = labels.get("severity")
                value = labels.get("value")
                summary = annotations.get("summary")
                description = annotations.get("description")

                if not all([team, severity, value, summary, description]):
                    print("[WARNING] Incomplete alert skipped.")
                    continue

                # Build alert data
                alert_data = {
                    "summary": summary,
                    "description": description,
                    "status": alert.get("status"),
                    "startsAt": alert.get("startsAt"),
                    "endsAt": alert.get("endsAt"),
                    "labels": labels,
                    "annotations": annotations
                }

                # Save to file
                team_dir = os.path.join(ALERT_DIR, team)
                os.makedirs(team_dir, exist_ok=True)
                file_path = os.path.join(team_dir, f"{severity}_{value}.json")

                try:
                    if os.path.exists(file_path):
                        with open(file_path, "r") as f:
                            existing = json.load(f)
                    else:
                        existing = []
                except Exception as e:
                    print(f"[ERROR] Failed to read file {file_path}: {e}")
                    existing = []

                existing.append(alert_data)

                try:
                    with open(file_path, "w") as f:
                        json.dump(existing, f, indent=2)
                except Exception as e:
                    print(f"[ERROR] Failed to write file {file_path}: {e}")

                # Send Telegram message
                message = (
                    f"*[{severity.upper()}]* alert for *{team}*\n\n"
                    f"*Summary:* {summary}\n"
                    f"*Description:* {description}\n"
                    f"*Value:* {value}"
                )
                send_telegram_message(message)

            except Exception as e:
                print(f"[ERROR] Failed to process alert: {e}")
                continue

        return jsonify({"message": "Alerts processed"}), 200

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        print(f"[FATAL] Internal error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Run server

app.run(port=5000, debug=True)
