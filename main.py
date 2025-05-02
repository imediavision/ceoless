from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Hardcoded values (replace with your actual credentials/URLs)
BOTPRESS_WEBHOOK_URL = "https://webhook.botpress.cloud/9f690c52-cca1-429d-bdd1-b821d1e33d50"
TELNYX_API_KEY = "KEY010967E6CBCC2E7B072AB667FBCDD9AD"
TELNYX_NUMBER = "+18778091002"

@app.route("/", methods=["GET"])
def index():
    return "Ceoless Webhook Listener is live."

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("Incoming from Telnyx:", data)

        # Safely extract values
        event_type = data.get("data", {}).get("event_type")
        message_text = data.get("data", {}).get("payload", {}).get("text")
        from_number = data.get("data", {}).get("from", {}).get("phone_number")

        if event_type != "message.received" or not message_text or not from_number:
            print("Ignored non-message event or missing fields.")
            return jsonify({"status": "ignored"}), 200

        payload = {
            "type": "text",
            "text": message_text,
            "channel": "telnyx",
            "from": from_number
        }

        print("Sending to Botpress:", payload)
        response = requests.post(BOTPRESS_WEBHOOK_URL, json=payload)
        print("Botpress response:", response.status_code, response.text)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error processing webhook:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=3000)


