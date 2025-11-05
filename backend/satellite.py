import time
import threading
import requests
from fastapi import FastAPI
from nfc_reader import (read_nfc, nfc_state)
from led_controller import (LEDController)
from sat_config import SATELLITE_ID, CORRECT_ID

# =====================
# CONFIG
# =====================
HUB_URL = "http://rpi4.local:8080/api/remote"   # <-- hub endpoint

led = LEDController()

# =====================
# FastAPI setup
# =====================
app = FastAPI()

# =====================
# NFC Logic
# =====================

game_active = False # game loop flag

def check_nfc_id(nfc_id: str):
    """Check NFC ID and return classification."""
    if not nfc_id:
        return None

    nfc_id = str(nfc_id)
    if nfc_id == CORRECT_ID:
        return "correct"
    else:
        return "wrong"


def nfc_processor():
    """Continuously poll NFC reader and send new detections to hub."""
    last_processed_id = None
    while True:
        current_read = nfc_state.get_reading()
        current_id = current_read.get("id")

        if game_active and current_id and current_id != last_processed_id:
            status = check_nfc_id(current_id)

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

@app.get("/led/red")
async def red_led():
    led.set_color((1, 0, 0))  # constant red
    return {"message": "Red LED on"}

@app.get("/led/green")
async def green_led():
    led.set_color((0, 1, 0))  # constant green
    return {"message": "Green LED on"}

@app.get("/api/unlock")
async def unlock_game():
    global game_active
    game_active = True
    print(f"[{SATELLITE_ID}] Game unlocked — ready to read NFCs")
    return {"message": "Game unlocked"}

@app.get("/api/lock")
async def lock_game():
    global game_active
    game_active = False
    print(f"[{SATELLITE_ID}] Game locked — NFCs ignored")
    led.turn_off()
    return {"message": "Game locked"}


# =====================
# Satellite reset endpoint
# =====================
@app.get("/api/reset")
async def reset_satellite():
    """
    Reset the satellite state after a game:
    - Turn off local LED
    - Reset last processed NFC ID
    - Reset local status
    """
    global last_processed_id
    global local_status

    # Reset the last processed NFC ID so repeated tags are sent again
    last_processed_id = None

    # Reset local status (if you use it)
    local_status = None

    # Turn off local LED
    led.turn_off()

    print(f"[{SATELLITE_ID}] Satellite reset completed")

    return {"message": f"{SATELLITE_ID} reset successful"}

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
    uvicorn.run(app, host="0.0.0.0", port=8080)
