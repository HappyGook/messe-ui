import time
import threading
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.nfc_reader import (read_nfc, nfc_state)
from led_controller import LEDController

# =====================
# CONFIG
# =====================
HUB_URL = "http://<MAIN_PI_IP>:8080/api/remote"   # <-- hub endpoint
SATELLITE_ID = "pi-zero-1"  # unique name/id for this RPi (change on each)

CORRECT_ID = "584186924480"
KNOWN_IDS = [
    "119591732478",
    "584186924480",
    "584182731423",
    "584192212898",
    "584183803890",
    "584184705952",
    "584183784382",
    "584185919748",
    "584195346115",
    "584184827296",
    "584195321184"
]

led = LEDController()

# =====================
# FastAPI setup
# =====================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# NFC Logic
# =====================
def check_nfc_id(nfc_id: str):
    """Check NFC ID and return classification."""
    if not nfc_id:
        return None

    nfc_id = str(nfc_id)
    if nfc_id == CORRECT_ID:
        return "correct"
    elif nfc_id in KNOWN_IDS:
        return "wrong"
    else:
        return "unknown"


def nfc_processor():
    """Continuously poll NFC reader and send new detections to hub."""
    last_processed_id = None
    while True:
        current_read = nfc_state.get_reading()
        current_id = current_read.get("id")

        if current_id and current_id != last_processed_id:
            status = check_nfc_id(current_id)
            if status == "correct":
                led.set_color((0, 1, 0)) # Green
            elif status=="wrong":
                led.set_color((1, 0, 0)) # Red
            else:
                led.set_color((0, 1, 1)) # Unknown (Blue)

            print(f"[{SATELLITE_ID}] Detected {status.upper()} ID: {current_id}")

            # send to hub
            try:
                requests.post(
                    HUB_URL,
                    json={
                        "satellite": SATELLITE_ID,
                        "id": current_id,
                        "status": status
                    },
                    timeout=2
                )
                print(f"[{SATELLITE_ID}] Sent result to hub")
            except Exception as e:
                print(f"[{SATELLITE_ID}] Failed to send to hub: {e}")

            last_processed_id = current_id

        time.sleep(0.1)


# =====================
# API ENDPOINTS
# =====================
@app.get("/status")
async def status():
    """Check that the satellite is alive."""
    return {"satellite": SATELLITE_ID, "status": "running"}

# =====================
# Startup threads
# =====================
@app.on_event("startup")
async def startup_event():
    nfc_thread = threading.Thread(target=read_nfc, daemon=True)
    processor_thread = threading.Thread(target=nfc_processor, daemon=True)

    nfc_thread.start()
    processor_thread.start()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)  # different port than hub
