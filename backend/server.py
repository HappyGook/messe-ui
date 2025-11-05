import asyncio
import os
import threading
import time
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from nfc_reader import nfc_state, read_nfc
from db import db
from led_controller import LEDController
import RPi.GPIO as GPIO

app = FastAPI()
led = LEDController()
led_lock = threading.Lock()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory status tracking
statuses = {
    "local": None,
    "stl1": None,
    "stl2": None,
    "stl3": None,
    "stl4": None
}

#TODO: correct ids are to be defined on RPIs
SATELLITE_IPS = {
    "stl1": "172.16.15.81:8080",
    "stl2": "172.16.15.82:8080",
    "stl3": "172.16.15.83:8080",
    "stl4": "172.16.15.84:8080"
}

CORRECT_ID = "584194412400"

BUZZER_PIN = 17
buzzer_clicked = False  # short-lived event flag
game_active = False # flag for game loop

all_statuses_initialized = False

def check_nfc_id(nfc_id):
    if not nfc_id:
        return None

    # Convert to string to ensure consistent comparison
    nfc_id = str(nfc_id)

    if nfc_id == CORRECT_ID:
        print(f"[NFC] CORRECT ID detected: {nfc_id}")
        return "correct"
    else:
        print(f"[NFC] WRONG ID detected: {nfc_id}")
        return "wrong"

class UserSave(BaseModel):
    name: str
    time: str

class NameCheck(BaseModel):
    name: str

class UserModify(BaseModel):
    id: int
    name: str
    time: str

# -----------------------
# Endpoint for satellites
# -----------------------
class RemoteNFC(BaseModel):
    satellite: str  # e.g., 'stl1'
    id: str
    status: str     # 'correct', 'wrong'

@app.post("/api/remote")
async def receive_remote(remote: RemoteNFC):
    global all_statuses_initialized

    if not game_active:
        print(f"[HUB] Ignoring {remote.satellite} update (game not active)")
        return {"message": "Game not active"}

    if remote.satellite not in statuses:
        print(f"[HUB] Unknown satellite: {remote.satellite}")
        return {"message": "Unknown satellite"}

    statuses[remote.satellite] = remote.status
    print(f"[HUB] Updated {remote.satellite} -> {remote.status}")

    # Always trigger evaluation when we have a status update
    if all(value is not None for value in statuses.values()):
        if not all_statuses_initialized:
            all_statuses_initialized = True

        asyncio.create_task(evaluate_and_trigger())

    return {"message": "Status updated"}


def local_nfc_processor():
    global all_statuses_initialized

    while True:
        if not game_active:
            time.sleep(0.1)
            continue

        current_read = nfc_state.get_reading()
        current_id = current_read.get("id")

        if current_id:
            status = check_nfc_id(current_id)
            statuses["local"] = status
            print(f"[HUB] Local reader -> {status}")

            # Always trigger evaluation when we have a status update
            if all(value is not None for value in statuses.values()):
                if not all_statuses_initialized:
                    all_statuses_initialized = True

                # Create a new event loop for this thread to run async code
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(evaluate_and_trigger())
                    loop.close()
                except Exception as e:
                    print(f"[NFC] Error running evaluate_and_trigger: {e}")

        time.sleep(0.1)


async def evaluate_and_trigger():
    """Check current statuses and trigger LEDs individually."""

    global statuses

    # --- Local LED ---
    local_status = statuses.get("local")
    with led_lock:
        if local_status == "correct":
            led.set_color((0, 1, 0))
        elif local_status == "wrong":
            led.set_color((1, 0, 0))
        else:
            led.turn_off()

    # --- Satellite LEDs ---
    async def trigger_satellite(name: str, i: int):
        status = statuses.get(name)
        if status == "correct":
            color_name = "green"
        elif status == "wrong":
            color_name = "red"
        else:
            return  # unknown/off, do nothing

        url = f"http://stl{i}.local:8080/led/{color_name}"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    print(f"[HUB] Triggered light on {name} ({color_name})")
                else:
                    print(f"[HUB] {name} responded with {response.status_code}")
        except Exception as e:
            print(f"[HUB] Failed to trigger {name}: {e}")

    satellites = [("stl1", 1), ("stl2", 2), ("stl3", 3), ("stl4", 4)]
    await asyncio.gather(*(trigger_satellite(name, i) for name, i in satellites))

    # --- Reset game state after victory ---
    if all(status == "correct" for status in statuses.values()):
        async def reset_game_state():
            await asyncio.sleep(3)

            global game_active
            game_active = False
            await asyncio.gather(*(lock_satellite(i) for i in range(1, 5)))
            print("[GAME] All correct — game locked and waiting for next start")

            # Reset in-memory statuses for a fresh game
            for key in statuses:
                statuses[key] = None

            # Notify satellites to reset last_processed_id so repeated tags are recognized
            await asyncio.gather(*(notify_satellite_reset(i) for i in range(1, 5)))

            # Reset global flag to allow next game
            global all_statuses_initialized
            all_statuses_initialized = False

            with led_lock:
                led.turn_off()

    print("[HUB] Game state fully reset, ready for next round")

    asyncio.create_task(reset_game_state())

def setup_buzzer():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    print(f"[BUZZER] Pin {BUZZER_PIN} ready for polling")

def buzzer_pressed(channel):
    print("[BUZZER] Button pressed (pin 15 -> LOW)")

# Unlock all satellites for the new game
async def notify_satellite_unlock(i: int):
    url = f"http://stl{i}.local:8080/api/unlock"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.get(url)
            print(f"[HUB] Unlocked stl{i}")
    except Exception as e:
        print(f"[HUB] Failed to unlock stl{i}: {e}")

async def lock_satellite(i: int):
    url = f"http://stl{i}.local:8080/api/lock"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.get(url)
            print(f"[HUB] Locked stl{i}")
    except Exception as e:
        print(f"[HUB] Failed to lock stl{i}: {e}")


async def notify_satellite_reset(i: int):
    url = f"http://stl{i}.local:8080/api/reset"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.get(url)
            print(f"[HUB] Notified stl{i} to reset last_processed_id")
    except Exception as e:
        print(f"[HUB] Failed to notify stl{i}: {e}")

async def reset_all_satellites():
    """Notify all satellites to reset their state."""
    print("[HUB] Resetting all satellites for new game...")

    await asyncio.gather(*(notify_satellite_reset(i) for i in range(1, 5)))

    # Reset local statuses and flags
    for key in statuses:
        statuses[key] = None
    global all_statuses_initialized
    all_statuses_initialized = False
    print("[HUB] Local statuses cleared and ready for new game")

async def buzzer_polling():
    global buzzer_clicked
    last_state = GPIO.input(BUZZER_PIN)
    print(f"[BUZZER] Starting poll. Initial state: {last_state}")

    while True:
        current_state = GPIO.input(BUZZER_PIN)

        if current_state != last_state:
            if current_state == 1:
                print("[BUZZER] Rising edge detected -> Button PRESSED")
                buzzer_clicked = True
                # Reset and start a new game
                await reset_all_satellites()  # await instead of asyncio.run
                global game_active
                game_active = True
                await asyncio.gather(*(notify_satellite_unlock(i) for i in range(1, 5)))
                print("[GAME] Game unlocked — NFC reads enabled!")
            elif current_state == 0:
                print("[BUZZER] Falling edge detected -> Button RELEASED")
                buzzer_clicked = False
                print(f"[BUZZER] buzzer_clicked reset to False on release")

            last_state = current_state

        await asyncio.sleep(0.05)  # await asyncio.sleep instead of time.sleep


# start-up event starts NFC reading
@app.on_event("startup")
async def startup_event():
    setup_buzzer()
    threading.Thread(target=read_nfc, daemon=True).start()
    threading.Thread(target=local_nfc_processor, daemon=True).start()

    # Create the buzzer polling task
    asyncio.create_task(buzzer_polling())

@app.on_event("shutdown")
async def shutdown_event():
    GPIO.cleanup()

# Test APIs for frontend
@app.get("/api/setbuzzer")
async def set_buzzer_status():
    global buzzer_clicked
    buzzer_clicked = True

@app.get("/api/setstatus")
async def set_statuses():
    statuses["local"]="correct"
    statuses["stl1"]="correct"
    statuses["stl2"]="correct"
    statuses["stl3"]="correct"
    statuses["stl4"]="correct"

# API endpoints
@app.get("/api/statuses")
async def get_statuses():
    return statuses

@app.get("/api/buzzer")
async def get_buzzer_status():
    global buzzer_clicked
    state = buzzer_clicked
    print(f"[API] /api/buzzer called -> buzzer_clicked={state}")
    if buzzer_clicked:
        buzzer_clicked = False  # reset flag immediately
        print("[API] buzzer_clicked reset to False after read")
    return {"clicked": state}

@app.post("/api/save")
async def save_user(user: UserSave):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, time) VALUES (?, ?)",
            (user.name, user.time)
        )
        conn.commit()
        return {"message": "User saved successfully", "userId": cursor.lastrowid}

@app.get("/api/leaderboard")
async def get_leaderboard():
    with db.get_connection() as conn:
        rows = conn.execute("""
                            SELECT id, name, time, created_at
                            FROM users
                            ORDER BY id
                            """).fetchall()
        return [dict(row) for row in rows]

@app.get("/api/leaderAll")
async def get_all_leaders():
    with db.get_connection() as conn:
        rows = conn.execute("""
                            SELECT id, name, time, created_at
                            FROM all_scores
                            ORDER BY id
                            """).fetchall()
        return [dict(row) for row in rows]

@app.post("/api/modifyAll")
async def modify_all(users: List[UserModify]):
    with db.get_connection() as conn:
        for user in users:
            conn.execute(
                "UPDATE all_scores SET name = ?, time = ? WHERE id = ?",
                (user.name, user.time, user.id)
            )
        conn.commit()
        return {"message": f"Successfully modified {len(users)} rows in all_scores"}

@app.post("/api/deleteAll")
async def delete_all(ids: List[int]):
    with db.get_connection() as conn:
        placeholders = ','.join('?' * len(ids))
        conn.execute(f"DELETE FROM all_scores WHERE id IN ({placeholders})", ids)
        conn.commit()
        return {"message": f"Successfully deleted {len(ids)} rows from all_scores"}

@app.post("/api/name")
async def check_name(user: NameCheck):
    with db.get_connection() as conn:
        # Check users table
        row1 = conn.execute("SELECT name FROM users WHERE name = ?", (user.name,)).fetchone()
        # Check all_scores table
        row2 = conn.execute("SELECT name FROM all_scores WHERE name = ?", (user.name,)).fetchone()

        if row1 or row2:
            raise HTTPException(status_code=400, detail="Name ist bereits vergeben")
        return {"success": True, "message": "Verfügbar!"}

@app.post("/api/reset")
async def reset_users_to_all_scores():
    with db.get_connection() as conn:
        # 1. Copy all users to all_scores
        conn.execute("""
                     INSERT INTO all_scores (name, time, created_at)
                     SELECT name, time, created_at FROM users
                     """)
        # 2. Delete all users from users table
        conn.execute("DELETE FROM users")
        conn.commit()
    return {"message": "All users moved to all_scores and cleared from users table"}

@app.post("/api/delete")
async def delete_users(ids: List[int]):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(ids))
        cursor.execute(f"DELETE FROM users WHERE id IN ({placeholders})", ids)
        conn.commit()
        return {"message": f"Successfully deleted {cursor.rowcount} rows"}

@app.post("/api/modify")
async def modify_users(users: List[UserModify]):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for user in users:
            cursor.execute(
                "UPDATE users SET name = ?, time = ? WHERE id = ?",
                (user.name, user.time, user.id)
            )
        conn.commit()
        return {"message": f"Successfully modified {len(users)} rows"}

@app.post("/api/add")
async def add_users(users: List[UserSave]):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for user in users:
            cursor.execute(
                "INSERT INTO users (name, time, created_at) VALUES (?, ?, datetime('now'))",
                (user.name, user.time)
            )
        conn.commit()
        return {"message": f"Successfully added {len(users)} rows"}

@app.get("/api/getall")
async def get_all_users():
    with db.get_connection() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("""
                              SELECT id, name, time, created_at
                              FROM users
                              ORDER BY id
                              """).fetchall()
        return [dict(row) for row in rows]

# Frontend serve after apis
dist_path = os.path.join(os.path.dirname(__file__), 'dist')
app.mount("/", StaticFiles(directory=dist_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)