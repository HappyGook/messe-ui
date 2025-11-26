import time
import threading
import requests
from fastapi import FastAPI, Request
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
    """Continuously poll NFC reader and send new detections to hub when game is active."""
    game_start_time = None
    last_sent_id = None  # Track what ID we last sent to avoid duplicate requests

    while True:
        if not game_active:
            game_start_time = None
            last_sent_id = None  # Reset when game becomes inactive
            time.sleep(0.1)
            continue

        # Track when game just started
        if game_start_time is None:
            game_start_time = time.time()

        current_read = nfc_state.get_reading()
        current_id = current_read.get("id")

        # Only process if we're past the grace period and ID has changed
        if (time.time() - game_start_time) > 0.5 and current_id != last_sent_id:

            if current_id:
                # New card detected
                status = check_nfc_id(current_id)
                print(f"[{SATELLITE_ID}] New ID detected: {status.upper()} - {current_id}")

                # Send to hub
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
                    print(f"[{SATELLITE_ID}] Sent new status to hub: {status}")
                    last_sent_id = current_id
                except Exception as e:
                    print(f"[{SATELLITE_ID}] Failed to send to hub: {e}")

            elif last_sent_id is not None:
                # Card was removed (current_id is None but we had sent something before)
                print(f"[{SATELLITE_ID}] Card removed - clearing status")

                try:
                    requests.post(
                        HUB_URL,
                        json={
                            "satellite": SATELLITE_ID,
                            "id": None,
                            "status": None
                        },
                        timeout=2
                    )
                    print(f"[{SATELLITE_ID}] Sent clear status to hub")
                    last_sent_id = None
                except Exception as e:
                    print(f"[{SATELLITE_ID}] Failed to send clear status to hub: {e}")

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

    # Clear NFC state completely
    nfc_state.last_read = {"id": None, "timestamp": None}

    game_active = True
    led.turn_off()  # Clear LED state
    print(f"[{SATELLITE_ID}] Game unlocked — NFC state cleared and ready to read NFCs")
    return {"message": "Game unlocked"}

@app.get("/api/lock")
async def lock_game():
    global game_active
    game_active = False

    # Clear NFC state completely
    nfc_state.last_read = {"id": None, "timestamp": None}

    led.turn_off()
    print(f"[{SATELLITE_ID}] Game locked — NFCs ignored")
    return {"message": "Game locked"}

@app.get("/api/reset")
async def reset_satellite():
    """Reset the satellite state after a game"""

    # Clear NFC state completely
    nfc_state.last_read = {"id": None, "timestamp": None}

    # Turn off local LED
    led.turn_off()
    print(f"[{SATELLITE_ID}] Satellite reset completed - NFC state cleared")
    return {"message": f"{SATELLITE_ID} reset successful"}

@app.post("/api/idle-start")
async def idle_start(req: Request):
    data = await req.json()
    start_ts = data.get("timestamp", time.time())  # fallback to local time if missing
    print(f"[IDLE] Starting idle mode at hub timestamp {start_ts}")
    led.start_idle_mode(start_ts)
    return {"status": "idle_started", "timestamp": start_ts}

@app.post("/api/idle-stop")
async def idle_stop():
    print(f"[IDLE] {SATELLITE_ID} is stopping the idle mode")
    led.stop_idle_mode()
    return {"status": "idle_stopped"}

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
