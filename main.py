import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Directly setting the Botpress webhook URL
BOTPRESS_URL = "https://webhook.botpress.cloud/5323dbbd-eb2f-43e6-9535-222a9b31a8ee"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Incoming Test Data:", data)

    # Forward the data to Botpress
    headers = {"Content-Type": "application/json"}
    response = requests.post(BOTPRESS_URL, headers=headers, json=data)

    print("Botpress response:", response.status_code)
    print("Botpress raw response:", response.text)
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)




