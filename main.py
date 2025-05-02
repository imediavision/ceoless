from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Hardcoded values
BOTPRESS_WEBHOOK_URL = "https://webhook.botpress.cloud/9f690c52-cca1-429d-bdd1-b821d1e33d50"
TELNYX_API_KEY = "KEY01967E6CBCC2E7B072AB667FBCDD9AD"
TELNYX_NUMBER = "+187789091002"

@app.route("/", methods=["GET"])
def index():
    return "Ceoless Webhook Listener is live."

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("📩 Incoming from Telnyx:", data)

        telnyx_data = data.get("data")
        print("DEBUG: data['data'] =", telnyx_data)

        if not telnyx_data:
            print("⚠️ 'data' field is missing or None.")
            return jsonify({"error": "'data' field is missing"}), 400

        event_type = telnyx_data.get("event_type")
        if event_type != "message.received":
            print("⚠️ Ignored non-message event or missing fields.")
            return jsonify({"status": "ignored"}), 200

        from_info = telnyx_data.get("from", {})
        print("DEBUG: from_info =", from_info)

        if isinstance(from_info, dict):
            sender_number = from_info.get("phone_number")
        else:
            print("⚠️ 'from' field is not a dict:", from_info)
            return jsonify({"error": "'from' field invalid"}), 400

        message_text = telnyx_data.get("text")
        print("📤 Sending to Botpress:", {"text": message_text, "channel": "telnyx", "from": sender_number})

        bp_payload = {
            "type": "text",
            "text": message_text,
            "channel": "telnyx",
            "from": sender_number
        }

        response = requests.post(BOTPRESS_WEBHOOK_URL, json=bp_payload)
        print("🤖 Botpress response:", response.status_code)

        try:
            bot_reply = response.json()
            reply_text = bot_reply.get("text")
        except Exception as parse_error:
            print("❌ Error parsing Botpress response:", parse_error)
            return jsonify({"error": "invalid bot response"}), 500

        if not reply_text:
            print("⚠️ No reply text from bot.")
            return jsonify({"error": "empty bot reply"}), 200

        sms_payload = {
            "from": TELNYX_NUMBER,
            "to": sender_number,
            "text": reply_text
        }

        headers = {
            "Authorization": f"Bearer {TELNYX_API_KEY}",
            "Content-Type": "application/json"
        }

        sms_response = requests.post("https://api.telnyx.com/v2/messages", json=sms_payload, headers=headers)
        print("📨 SMS sent via Telnyx:", sms_response.status_code, sms_response.text)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error in webhook handler:", e)
        return jsonify({"error": "internal error"}), 500

