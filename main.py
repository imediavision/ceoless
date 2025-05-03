import os
import json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOTPRESS_URL = os.environ.get("BOTPRESS_URL")  # Example: https://webhook.botpress.cloud/your-bot-id
TELNYX_API_KEY = os.environ.get("TELNYX_API_KEY")
FROM_NUMBER = os.environ.get("TELNYX_FROM_NUMBER")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📩 Incoming from Telnyx:", data)

    try:
        payload = data["data"]["payload"]
        user_text = payload["text"]
        user_phone = payload["from"]["phone_number"]
    except Exception as e:
        print("❌ Failed to parse incoming SMS:", e)
        return "Invalid format", 400

    # Build Botpress payload
    bot_request = {
        "type": "text",
        "channel": "telnyx",
        "from": user_phone,
        "payload": {
            "text": user_text
        }
    }

    try:
        bp_response = requests.post(BOTPRESS_URL, json=bot_request)
        print("📬 Botpress response:", bp_response.status_code)
        print("🧾 Botpress raw response:", bp_response.text)
        bot_response = bp_response.json()
    except Exception as e:
        print("❌ Error talking to Botpress:", e)
        return "Botpress error", 500

    # Get reply text from Botpress
    bot_text = bot_response.get("payload", {}).get("text", "Sorry, I didn't get that.")

    # Send reply back through Telnyx
    sms_data = {
        "from": FROM_NUMBER,
        "to": user_phone,
        "text": bot_text
    }

    try:
        telnyx_response = requests.post(
            "https://api.telnyx.com/v2/messages",
            headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
            json=sms_data
        )
        print("📤 SMS sent via Telnyx:", telnyx_response.status_code, telnyx_response.text)
    except Exception as e:
        print("❌ Failed to send SMS:", e)
        return "SMS send error", 500

    return "OK", 200

@app.route("/", methods=["GET"])
def health():
    return "OK", 200


