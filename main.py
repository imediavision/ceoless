from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Updated Botpress Webhook URL
BOTPRESS_WEBHOOK_URL = "https://webhook.botpress.cloud/9f690c52-cca1-429d-bdd1-b821d1e33d50"
TELNYX_API_KEY = "KEY0123456789ABCDEF"  # Use your real API key here
TELNYX_NUMBER = "+18778901002"  # Your Telnyx number

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
            text = data["data"]["payload"]["text"]
            from_number = data["data"]["from"]["phone_number"]

            payload = {
                "type": "text",
                "text": text,
                "channel": "telnyx",
                "from": from_number,
            }

            print("Sending to Botpress:", payload)
            response = requests.post(BOTPRESS_WEBHOOK_URL, json=payload)
            print("Botpress response:", response.status_code)

            return jsonify({"success": True}), 200
        else:
            print("Unhandled event type:", event_type)
            return jsonify({"success": False, "reason": "Unhandled event type"}), 400

    except Exception as e:
        print("Error processing webhook:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=3000)


