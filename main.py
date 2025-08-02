from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flask_socketio import SocketIO
import requests # Make sure to add 'requests' to your requirements.txt
import os

app = Flask(__name__)
CORS(app) 
socketio = SocketIO(app, cors_allowed_origins="*")

trade_status = {"status": "0"}

@app.route("/status", methods=["GET"])
def get_status():
    return jsonify(trade_status)

@app.route("/status", methods=["POST"])
def set_status():
    data = request.json
    if data and "status" in data:
        trade_status["status"] = data.get("status", "0")
        print(f"Status updated to: {trade_status['status']}")
        socketio.emit('status_update', trade_status)
        return jsonify(success=True, new_status=trade_status["status"])
    return jsonify(success=False, error="Invalid data format"), 400

# NEW: Endpoint for handling webhook notifications
@app.route("/notify", methods=["POST"])
def handle_notification():
    data = request.json
    webhook_url = data.get("webhook_url")
    embed = data.get("embed")

    if not webhook_url or not embed:
        return jsonify(success=False, error="Missing webhook_url or embed data"), 400

    # The server sends the webhook to Discord, not the client
    try:
        requests.post(webhook_url, json={"embeds": [embed]})
        print("Successfully forwarded webhook to Discord.")
        return jsonify(success=True)
    except Exception as e:
        print(f"Error sending webhook: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route("/", methods=["GET"])
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trade Signal Control</title>
        <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                background-color: #1e1e1e; 
                color: #d4d4d4; 
                margin: 0; 
            }
            .container { 
                text-align: center; 
                background-color: #252526; 
                padding: 40px; 
                border-radius: 10px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                border: 1px solid #3c3c3c;
            }
            h1 { 
                margin-top: 0; 
                color: #cccccc;
            }
            #status { 
                font-size: 2.5em; 
                font-weight: bold; 
                margin: 20px 0; 
                padding: 15px 25px; 
                background-color: #1e1e1e; 
                border-radius: 5px; 
                border: 1px solid #3c3c3c;
                min-width: 150px;
                display: inline-block;
                transition: color 0.3s, border-color 0.3s;
            }
            .status-active { color: #4CAF50; border-color: #4CAF50; }
            .status-inactive { color: #d16a6a; border-color: #d16a6a; }
            button { 
                background-color: #d16a6a; 
                color: white; 
                border: none; 
                padding: 15px 30px; 
                font-size: 1em; 
                border-radius: 5px; 
                cursor: pointer; 
                transition: background-color 0.3s; 
                font-weight: bold;
            }
            button:hover { background-color: #b85656; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Trade Signal Status</h1>
            <div id="status">Loading...</div>
            <button id="resetButton">Reset Status to 0</button>
        </div>
        <script>
            const statusDiv = document.getElementById('status');
            const resetButton = document.getElementById('resetButton');
            const socket = io();

            function updateStatusDisplay(status) {
                statusDiv.textContent = `${status}`;
                statusDiv.className = status === '1' ? 'status-active' : 'status-inactive';
            }

            socket.on('status_update', (data) => updateStatusDisplay(data.status));

            async function fetchInitialStatus() {
                try {
                    const response = await fetch('/status');
                    const data = await response.json();
                    updateStatusDisplay(data.status);
                } catch (error) {
                    console.error('Error fetching initial status:', error);
                    statusDiv.textContent = 'Error';
                }
            }

            async function resetStatus() {
                try {
                    await fetch('/status', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ status: '0' })
                    });
                } catch (error) {
                    console.error('Error resetting status:', error);
                }
            }

            resetButton.addEventListener('click', resetStatus);
            fetchInitialStatus();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    socketio.run(app, host="0.0.0.0", port=port)
