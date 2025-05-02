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

        event_type = data.get("data", {}).get("event_type")
        if event_type != "message.received":
            print("Ignored non-message event or missing fields.")
            return jsonify({"status": "ignored"}), 200

        text = data["data"]["payload"]["text"]
        from_number = data["data"]["payload"]["from"]["phone_number"]

        # Send to Botpress
        payload = {
            "type": "text",
            "text": text,
            "channel": "telnyx",
            "from": from_number
        }

        print("Sending to Botpress:", payload)
        response = requests.post(BOTPRESS_WEBHOOK_URL, json=payload)
        print("Botpress response:", response.status_code)

        # Parse Botpress response
        reply_text = "Thanks!"
        try:
            bp_response = response.json()
            reply_text = bp_response.get("responses", [{}])[0].get("text", "Thanks!")
        except Exception as e:
            print("Error parsing Botpress response:", e)

        # Send reply via Telnyx
        sms_payload = {
            "from": TELNYX_NUMBER,
            "to": from_number,
            "text": reply_text
        }

        sms_response = requests.post(
            "https://api.telnyx.com/v2/messages",
            headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
            json=sms_payload
        )

        print("SMS sent via Telnyx:", sms_response.status_code, sms_response.text)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=3000)


