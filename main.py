import os
import json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOTPRESS_URL = os.environ.get("BOTPRESS_URL")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📩 Incoming Test Data:", json.dumps(data, indent=2))

    try:
        payload = data["data"]["payload"]
        user_text = payload["text"]
        user_phone = payload["from"]["phone_number"]
    except Exception as e:
        print("❌ Failed to parse test data:", e)
        return "Invalid format", 400

    bot_request = {
        "type": "text",
        "text": user_text,
        "channel": "webhook",
        "userId": user_phone
    }

    try:
        bp_response = requests.post(BOTPRESS_URL, json=bot_request)
        print("📬 Botpress response:", bp_response.status_code)
        print("🧾 Botpress raw response:", bp_response.text)
    except Exception as e:
        print("❌ Error talking to Botpress:", e)
        return "Botpress error", 500

    return "OK", 200

@app.route("/", methods=["GET"])
def health():
    return "OK", 200



