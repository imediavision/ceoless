import os
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

BOTPRESS_URL = "https://webhook.botpress.cloud/9f690c52-cca1-429d-bdd1-b821d1e33d50"
TELNYX_API_KEY = "KEY0196927FCBC0D2DA1F3E1766FE185297_NiJwOYI8ZNN9khnG6vJSpG"

@app.route("/")
def index():
    return "OK"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"📩 Incoming from Telnyx: {data}")

    try:
        data = data.get("data", {})
        logging.debug(f"DEBUG: data['data'] = {data}")

        payload = data.get("payload", {})
        from_info = payload.get("from") or {}
        logging.debug(f"DEBUG: from_info = {from_info}")

        if not isinstance(from_info, dict):
            logging.warning("⚠️ 'from' field is not a dict: %s", from_info)
            return "Ignored non-message event or missing fields.", 400

        message_text = payload.get("text")
        sender_number = from_info.get("phone_number")

        payload_to_botpress = {
            "text": message_text,
            "channel": "telnyx",
            "from": sender_number
        }
        logging.info(f"📤 Sending to Botpress: {payload_to_botpress}")

        res = requests.post(BOTPRESS_URL, json=payload_to_botpress)
        logging.info(f"🤖 Botpress response: {res.status_code}")

        try:
            bot_response = res.json()
        except Exception as e:
            logging.error(f"❌ Error parsing Botpress response: {e}")
            return "", 200

        if not bot_response:
            return "", 200

        text = bot_response.get("payload", {}).get("text")
        if not text:
            return "", 200

        telnyx_res = requests.post(
            "https://api.telnyx.com/v2/messages",
            headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
            json={
                "from": payload.get("to", [{}])[0].get("phone_number"),
                "to": sender_number,
                "text": text
            }
        )
        logging.info(f"📬 SMS sent via Telnyx: {telnyx_res.status_code} {telnyx_res.text}")

    except Exception as e:
        logging.exception(f"❌ Webhook error: {e}")
        return f"Webhook error: {e}", 500

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
