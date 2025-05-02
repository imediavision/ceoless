from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Hardcoded values
BOTPRESS_WEBHOOK_URL = "https://ceoless.botpress.cloud/webhooks/5aeb2bc4-1776-4f68-87df-f2eacccaa9a6"
TELNYX_API_KEY = "KEY01967E6CBCC2E7B072ABA667FBCDD9AD"
TELNYX_NUMBER = "+18778091002"

@app.route("/", methods=["GET"])
def index():
    return "Ceoless Webhook Listener is live."

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("Incoming from Telnyx:", data)

        event_type = data.get("data", {}).get("event_type")
        if event_type == "message.received":
            message_text = data.get("data", {}).get("payload", {}).get("text", "")
            sender = data.get("data", {}).get("payload", {}).get("from", {}).get("phone_number", "unknown")

            outgoing = {
                "type": "text",
                "text": message_text,
                "channel": "telnyx",
                "from": sender
            }

            print("Sending to Botpress:", outgoing)
            botpress_response = requests.post(BOTPRESS_WEBHOOK_URL, json=outgoing)
            print("Botpress response:", botpress_response.status_code)
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Webhook error:", str(e))
        return jsonify({"status": "error", "detail": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

