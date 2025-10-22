import asyncio
import threading
import time

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from nfc_reader import nfc_state, read_nfc
from db import db
from led_controller import LEDController
import RPi.GPIO as GPIO

app = FastAPI()
led = LEDController()

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

#TODO: correct tags are to be defined on HUB RPi
CORRECT_ID = "584186924480"  # I chose this one as the "correct" ID
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

BUZZER_PIN = 15
buzzer_clicked = False  # short-lived event flag

all_statuses_initialized = False

def check_nfc_id(nfc_id):
    if not nfc_id:
        return None

    # Convert to string to ensure consistent comparison
    nfc_id = str(nfc_id)

    if nfc_id == CORRECT_ID:
        print(f"[NFC] CORRECT ID detected: {nfc_id}")
        return "correct"
    elif nfc_id in KNOWN_IDS:
        print(f"[NFC] WRONG ID detected: {nfc_id}")
        return "wrong"
    else:
        print(f"[NFC] UNKNOWN ID detected: {nfc_id}")
        return "unknown"

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
    status: str     # 'correct', 'wrong', 'unknown'

@app.post("/api/remote")
async def receive_remote(remote: RemoteNFC):
    global all_statuses_initialized

    if remote.satellite not in statuses:
        print(f"[HUB] Unknown satellite: {remote.satellite}")
        return {"message": "Unknown satellite"}

    statuses[remote.satellite] = remote.status
    print(f"[HUB] Updated {remote.satellite} -> {remote.status}")

    if all(value is not None for value in statuses.values()):
        if not all_statuses_initialized:
            # First time all statuses are available
            all_statuses_initialized = True
            asyncio.create_task(evaluate_and_trigger())
        else:
            # Evaluate every update after first as well
            asyncio.create_task(evaluate_and_trigger())

    return {"message": "Status updated"}


def local_nfc_processor():
    last_id = None
    global all_statuses_initialized

    while True:
        current_read = nfc_state.get_reading()
        current_id = current_read.get("id")
        if current_id and current_id != last_id:
            status = check_nfc_id(current_id)
            statuses["local"] = status
            print(f"[HUB] Local reader -> {status}")
            last_id = current_id

            # Trigger LEDs if all statuses known
            if all(value is not None for value in statuses.values()):
                if not all_statuses_initialized:
                    all_statuses_initialized = True
                    asyncio.run(evaluate_and_trigger())
                else:
                    asyncio.run(evaluate_and_trigger())
        time.sleep(0.1)


async def evaluate_and_trigger():
    """Check current statuses and trigger LEDs on satellites."""
    global statuses

    # Determine color
    if all(status == "correct" for status in statuses.values()):
        color = "green"
    else:
        color = "red"

    # Local LED
    led.blink_color((0, 1, 0) if color=="green" else (1, 0, 0), times=3)

    # Satellite LEDs
    for i in range(1,4):
        url = f"http://stl{i}/led/{color}"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    print(f"[HUB] Triggered {color} on stl{i}")
                else:
                    print(f"[HUB] stl{i} responded {resp.status_code}")
        except Exception as e:
            print(f"[HUB] Failed to trigger stl{i}: {e}")


def setup_buzzer():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Event detection for button press (HIGH -> LOW)
    GPIO.add_event_detect(BUZZER_PIN, GPIO.FALLING, callback=buzzer_pressed, bouncetime=200)

def buzzer_pressed(channel):
    print("[BUZZER] Button pressed (pin 15 -> LOW)")

    import asyncio
    asyncio.create_task(trigger_color())

async def trigger_color():
    color="green"
    for status in statuses.values():
        if status !="correct":
            color="red"
            break

    # Local LED blinking
    if color=="green":
        led.blink_color((0, 1, 0), times=3)
    else:
        led.blink_color((1, 0, 0), times=3)

    # Satellites LED blinking
    for i in range(1,4):
        url = f"http://stl{i}.local:8080/led/{color}"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    print(f"[HUB] Triggered light on stl{i}")
                else:
                    print(f"[HUB] stl{i} responded with {response.status_code}")
        except Exception as e:
            print(f"[HUB] Failed to trigger stl{i}: {e}")

# start-up event starts NFC reading
@app.on_event("startup")
async def startup_event():
    setup_buzzer()
    threading.Thread(target=read_nfc, daemon=True).start()
    threading.Thread(target=local_nfc_processor, daemon=True).start()

@app.on_event("shutdown")
async def shutdown_event():
    GPIO.cleanup()


# API endpoints
@app.get("/api/statuses")
async def get_statuses():
    return statuses

@app.get("/api/buzzer")
async def get_buzzer_status():
    global buzzer_clicked
    state = buzzer_clicked
    if buzzer_clicked:
        buzzer_clicked = False  # reset flag immediately
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)