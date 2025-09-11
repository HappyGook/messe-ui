#!/usr/bin/env python
# import libraries
import gpiozero
from mfrc522 import SimpleMFRC522
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import threading
import json

# initialize object for rfid module
reader = SimpleMFRC522()

#class to store NFC
class NFCState:
    def __init__(self):
        self.last_read = {
            "id": None,
            "text": None,
            "time": None
        }
        self.lock = threading.Lock()

    def update(self, nfc_id, text):
        with self.lock:
            self.last_read = {
                "id": nfc_id,
                "text": text,
                "time": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    def get_reading(self):
        with self.lock:
            return dict(self.last_read)

nfc_state = NFCState()

# Function to continuously read NFC tags
def read_nfc():
    print("NFC Reader started. Waiting for tags...")
    while True:
        try:
            # get id and text from tag
            nfc_id, text = reader.read()

            # print tag id and text
            nfc_state.update(nfc_id, text)

            print("\nTag detected!")
            print(f"ID: {nfc_id}")
            print(f"Text: {text}")
            print("\nWaiting for next tag...")

            # Small delay to prevent excessive CPU usage
            time.sleep(0.5)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error reading NFC: {e}")
            time.sleep(1)

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data":
            # Return JSON data
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(nfc_state.get_reading()), "utf-8"))
        else:
            # Return HTML page
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>NFC Reader Interface</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }
                    .nfc-display {
                        border: 1px solid #ccc;
                        padding: 20px;
                        border-radius: 5px;
                        margin-top: 20px;
                    }
                    .status {
                        color: green;
                        font-weight: bold;
                    }
                    .reading {
                        margin-top: 10px;
                        white-space: pre-wrap;
                    }
                </style>
            </head>
            <body>
                <h1>NFC Reader Interface</h1>
                <div class="nfc-display">
                    <p class="status">Reader Status: Active</p>
                    <div class="reading" id="nfcReading">Waiting for tag...</div>
                </div>

                <script>
                    function updateNFCReading() {
                        fetch('http://localhost:8080/data')
                            .then(response => response.json())
                            .then(data => {
                                if (data.id) {
                                    const reading = `Last Reading:
                                        ID: ${data.id}
                                        Text: ${data.text}
                                        Time: ${data.timestamp}`;
                                    document.getElementById('nfcReading').textContent = reading;
                                }
                            })
                            .catch(error => console.error('Error:', error));
                    }

                    // Update every second
                    setInterval(updateNFCReading, 1000);
                </script>
            </body>
            </html>
            """
            self.wfile.write(bytes(html, "utf-8"))


if __name__ == "__main__":
    # Start NFC reader in a separate thread
    nfc_thread = threading.Thread(target=read_nfc, daemon=True)
    nfc_thread.start()

    # Start web server
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")