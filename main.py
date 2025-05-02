from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Hardcoded values
BOTPRESS_WEBHOOK_URL = "https://webhook.botpress.cloud/9f690c52-cca1-429d-bdd1-b821d1e33d50"
TELNYX_API_KEY = "KEY01967E6CBCC2E7B072ABA667FBCDD9AD"
TELNYX_NUMBER = "+18778091002"

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
            print("ℹ️ Ignored non-message event or missing fields.")
            return jsonify({"status": "ignored"}), 200

        text = data["data"].get("text", "")
        from_info = data["data"].get("from")

        if isinstance(from_info, dict):
            sender_number = from_info.get("phone_number")
        else:
            print("⚠️ 'from' field is not a dict:", from_info)
            return jsonify({"error": "'from' field invalid"}), 400

        print("📤 Sending to Botpress:", {"text": text, "channel": "telnyx", "from": sender_number})
        botpress_response = requests.post(
            BOTPRESS_WEBHOOK_URL,
            json={"text": text, "channel": "telnyx", "from": sender_number}
        )

        print("🤖 Botpress response:", botpress_response.status_code)
        botpress_text = botpress_response.text.strip()
        if botpress_response.status_code == 200 and botpress_text:
            try:
                reply = botpress_response.json()
                if isinstance(reply, dict):
                    reply_text = reply.get("text", botpress_text)
                else:
                    reply_text = botpress_text
            except Exception as e:
                print("⚠️ Error parsing Botpress response:", e)
                reply_text = botpress_text

            sms_response = requests.post(
                "https://api.telnyx.com/v2/messages",
                headers={
                    "Authorization": f"Bearer {TELNYX_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": TELNYX_NUMBER,
                    "to": sender_number,
                    "text": reply_text
                }
            )
            print("📲 SMS sent via Telnyx:", sms_response.status_code, sms_response.text)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error processing webhook:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=3000)
