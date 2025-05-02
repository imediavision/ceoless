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

        event_type = data.get("data", {}).get("event_type")
        if event_type != "message.received":
            print("⚠️ Ignored non-message event or missing fields.")
            return "", 200

        message_text = data["data"]["payload"]["text"]
        sender_number = data["data"]["from"]["phone_number"]

        print("➡️ Sending to Botpress:", {"text": message_text, "from": sender_number})

        botpress_response = requests.post(
            BOTPRESS_WEBHOOK_URL,
            json={"type": "text", "text": message_text, "channel": "telnyx", "from": sender_number},
            headers={"Content-Type": "application/json"}
        )

        print("🤖 Botpress response:", botpress_response.status_code)
        try:
            reply_text = botpress_response.json().get("messages", [{}])[0].get("text", "")
        except ValueError:
            print("⚠️ Botpress returned non-JSON or empty body")
            reply_text = ""

        if not reply_text:
            print("⚠️ No reply from Botpress.")
            return "", 200

        print("📤 Sending via Telnyx:", reply_text)
        telnyx_response = requests.post(
            "https://api.telnyx.com/v2/messages",
            json={
                "from": TELNYX_NUMBER,
                "to": sender_number,
                "text": reply_text
            },
            headers={
                "Authorization": f"Bearer {TELNYX_API_KEY}",
                "Content-Type": "application/json"
            }
        )

        print("📬 Telnyx response:", telnyx_response.status_code, telnyx_response.text)
        return "", 200

    except Exception as e:
        print("❌ Webhook error:", e)
        return jsonify({"error": str(e)}), 500

