import os
import logging
from flask import Flask, request
import requests

app = Flask(__name__)

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telnyx and Botpress config (replace with your actual credentials and numbers)
TELNYX_API_KEY = "KEY0196927FCBC0D2DA1F3E1766FE185297_NiJwOYI8ZNN9khnG6vJSpG"
TELNYX_PHONE_NUMBER = "+18778091002"
BOTPRESS_WEBHOOK_URL = "https://webhook.botpress.cloud/9f690c52-cca1-429d-bdd1-b821d1e33d50"

@app.route("/")
def index():
    return "OK"

@app.route("/webhook", methods=["POST"])
def telnyx_webhook():
    try:
        data = request.json
        logger.info(f"📩 Incoming from Telnyx: {data}")

        event = data.get("data", {})
        payload = event.get("payload", {})
        from_info = payload.get("from", {})
        from_number = from_info.get("phone_number")
        text = payload.get("text")

        logger.debug(f"DEBUG: data['data'] = {event}")
        logger.debug(f"DEBUG: from_info = {from_info}")

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

        reply_text = "Sorry, I didn't get that."
        if bp_response.text.strip():
            try:
                reply = bp_response.json()
                reply_text = reply.get("text", reply_text)
            except Exception as e:
                logger.error(f"❌ Failed to parse Botpress JSON: {e}")
        else:
            logger.warning("⚠️ Botpress returned an empty response body.")

        # Send SMS back
        telnyx_payload = {
            "from": TELNYX_PHONE_NUMBER,
            "to": from_number,
            "text": reply_text
        }
        telnyx_response = requests.post(
            "https://api.telnyx.com/v2/messages",
            headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
            json=telnyx_payload
        )
        logger.info(f"📬 SMS sent via Telnyx: {telnyx_response.status_code} {telnyx_response.text}")

        return "ok", 200

    except Exception as e:
        logger.exception(f"❌ Webhook exception: {e}")
        return "error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
