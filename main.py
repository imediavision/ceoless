import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOTPRESS_URL = os.getenv("BOTPRESS_URL")  # e.g. https://webhook.botpress.cloud/...

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



