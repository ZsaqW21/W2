from flask import Flask, request, jsonify
from flask_cors import CORS
import requests # Make sure to add 'requests' to your requirements.txt
import os

app = Flask(__name__)
CORS(app) 

# Endpoint for handling webhook notifications from the Roblox script
@app.route("/notify", methods=["POST"])
def handle_notification():
    """This endpoint receives data from the Roblox script and forwards it to Discord."""
    data = request.json
    webhook_url = data.get("webhook_url")
    embed = data.get("embed")

    if not webhook_url or not embed:
        return jsonify(success=False, error="Missing webhook_url or embed data"), 400

    # The server sends the webhook to Discord, not the client
    try:
        # The payload for Discord requires the 'embeds' key to be a list
        discord_payload = {"embeds": [embed]}
        requests.post(webhook_url, json=discord_payload)
        print("Successfully forwarded webhook to Discord.")
        return jsonify(success=True)
    except Exception as e:
        print(f"Error sending webhook: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route("/", methods=["GET"])
def index():
    """This route serves a simple status page to confirm the server is running."""
    return "Webhook Proxy Server is running."

if __name__ == "__main__":
    # Railway and other providers set the PORT environment variable.
    # Default to 8080 for local testing.
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
