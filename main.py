from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Hardcoded values
BOTPRESS_WEBHOOK_URL = "https://webhook.botpress.cloud/9f690c52-cca1-429d-bdd1-b821d1e33d50"
TELNYX_API_KEY = "KEY01967E6CBCC2E7B072AB667FBCDD9AD"
TELNYX_NUMBER = "+18778091002"

@app.route("/", methods=["GET"])
def index():
    return "Ceoless Webhook Listener is live."

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("Incoming from Telnyx:", data)

        event = data.get("data", {})
        if event.get("event_type") != "message.received":
            print("Ignored non-message event")
            return jsonify({"status": "ignored"}), 200

        text = event.get("payload", {}).get("text")
        if not text:
            print("Ignored message with no text")
            return jsonify({"status": "ignored"}), 200

        from_number = event.get("from", {}).get("phone_number")
        print("Sending to Botpress:", {"text": text, "from": from_number})

        response = requests.post(BOTPRESS_WEBHOOK_URL, json={
            "type": "text",
            "text": text,
            "channel": "telnyx",
            "from": from_number
        })

        print("Botpress response:", response.status_code)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500



