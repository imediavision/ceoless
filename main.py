from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Hardcoded Botpress Webhook URL
BOTPRESS_WEBHOOK_URL = "https://webhook.botpress.cloud/9f690c52-cca1-429d-bdd1-b821d1e33d50"

# Hardcoded Telnyx API Key (replace with your actual key)
TELNYX_API_KEY = "KEY4a1c41e1a6f8e40fbb6b2d11c44cb14e_U5zDQMoZThGUtWTpZKjvBy"

@app.route("/")
def home():
    return "Ceoless webhook service running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Incoming from Telnyx:", data)

    if not data or "data" not in data:
        print("⚠️ Invalid webhook data")
        return jsonify({"status": "error", "message": "Invalid webhook data"}), 400

    telnyx_data = data["data"]
    payload = telnyx_data.get("payload", {})
    from_info = payload.get("from", {})
    print("DEBUG: from_info =", from_info)

    sender_number = from_info.get("phone_number")
    message_text = payload.get("text")

    if not message_text or not sender_number:
        print("⚠️ Missing message text or sender number")
        return jsonify({"status": "ignored"}), 200

    botpress_payload = {
        "text": message_text,
        "channel": "telnyx",
        "from": sender_number
    }

    print("📤 Sending to Botpress:", botpress_payload)

    try:
        response = requests.post(BOTPRESS_WEBHOOK_URL, json=botpress_payload)
        print("🤖 Botpress response:", response.status_code)

        # Try to read Botpress response
        bot_reply = response.json()
        reply_text = bot_reply.get("payload", {}).get("text", "Sorry, I couldn't understand that.")
    except Exception as e:
        print("❌ Error parsing Botpress response:", e)
        reply_text = "There was an error processing your message."

    # Send reply back to sender via Telnyx
    telnyx_response = requests.post(
        "https://api.telnyx.com/v2/messages",
        headers={
            "Authorization": f"Bearer {TELNYX_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": "+18778091002",  # your Telnyx number
            "to": sender_number,
            "text": reply_text
        }
    )

    print("📬 SMS sent via Telnyx:", telnyx_response.status_code, telnyx_response.text)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True)
