from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Hardcoded values
BOTPRESS_WEBHOOK_URL = "https://ceoless.botpress.cloud/webhooks/5aeb2bc4-1776-4f68-87df-f2eacccaa9a6"
TELNYX_API_KEY = "KEY01967E6CBCC2E7B07A2BA667FBCDD9AD"
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
        if event_type != "message.received":
            return jsonify({"status": "ignored"}), 200

        text = data["data"]["payload"]["text"]
        from_number = data["data"]["from"]["phone_number"]

        botpress_payload = {
            "type": "text",
            "text": text,
            "channel": "telnyx",
            "from": from_number
        }

        # Send to Botpress
        print("Sending to Botpress:", botpress_payload)
        bp_response = requests.post(BOTPRESS_WEBHOOK_URL, json=botpress_payload)
        print("Botpress response:", bp_response.status_code)

        if bp_response.status_code != 200:
            return jsonify({"error": "Botpress error"}), 500

        reply_data = bp_response.json()
        reply_text = reply_data.get("text", "Thanks!")

        # Send SMS reply via Telnyx
        send_sms_reply(from_number, reply_text)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Webhook error:", e)
        return jsonify({"error": str(e)}), 500

def send_sms_reply(to_number, message):
    print(f"Sending SMS to {to_number}: {message}")
    telnyx_payload = {
        "from": TELNYX_NUMBER,
        "to": to_number,
        "text": message
    }
    headers = {
        "Authorization": f"Bearer {TELNYX_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post("https://api.telnyx.com/v2/messages", json=telnyx_payload, headers=headers)
    print("Telnyx send response:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(port=3000)
