import os
import logging
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# Config
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY", "KEY...")  # Replace with actual if not using env vars
TELNYX_PHONE_NUMBER = os.getenv("TELNYX_PHONE_NUMBER", "+18778091002")
BOTPRESS_WEBHOOK_URL = os.getenv("BOTPRESS_WEBHOOK_URL", "https://webhook.botpress.cloud/YOUR_ID")

@app.route("/")
def index():
    return "OK"

@app.route("/webhook", methods=["POST"])
def webhook():
    print("⚡️ Webhook hit!")  # <--- KEY DIAGNOSTIC LOG
    try:
        data = request.get_json()
        logger.info(f"📩 Incoming from Telnyx: {data}")

        event = data.get("data", {})
        payload = event.get("payload", {})
        from_info = payload.get("from", {})
        from_number = from_info.get("phone_number")
        text = payload.get("text")

        if not from_number or not text:
            logger.warning("⚠️ Missing from_number or text")
            return "ignored", 200

        # Send to Botpress
        bp_payload = {
            "text": text,
            "channel": "telnyx",
            "from": from_number
        }

        logger.info(f"📤 Sending to Botpress: {bp_payload}")
        bp_response = requests.post(BOTPRESS_WEBHOOK_URL, json=bp_payload)
        logger.info(f"🤖 Botpress response: {bp_response.status_code}")

        if bp_response.text.strip():
            try:
                reply = bp_response.json()
                telnyx_payload = {
                    "from": TELNYX_PHONE_NUMBER,
                    "to": from_number,
                    "text": reply.get("text", "Sorry, I didn't get that.")
                }
                telnyx_response = requests.post(
                    "https://api.telnyx.com/v2/messages",
                    headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
                    json=telnyx_payload
                )
                logger.info(f"📬 SMS sent via Telnyx: {telnyx_response.status_code} {telnyx_response.text}")
            except Exception as e:
                logger.error(f"❌ Failed to parse Botpress JSON: {e}")
        else:
            logger.warning("⚠️ Botpress returned an empty response body.")

        return "ok", 200

    except Exception as e:
        logger.exception(f"❌ Webhook exception: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

