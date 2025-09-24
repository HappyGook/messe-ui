import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from nfc_reader import nfc_state, logger
from db import db

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# list of nfc tags
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

def check_nfc_id(nfc_id):
    if not nfc_id:
        return None

    # Convert to string to ensure consistent comparison
    nfc_id = str(nfc_id)

    if nfc_id == CORRECT_ID:
        print(f"[NFC] CORRECT ID detected: {nfc_id}")
        # here will be some project-relevant code
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

# start-up event starts NFC reading
@app.on_event("startup")
async def startup_event():
    # Start NFC reader in a separate thread
    import threading
    from nfc_reader import read_nfc

    def nfc_processor():
        last_processed_id = None
        while True:
            current_read = nfc_state.get_reading()
            current_id = current_read.get("id")

            # Only process if we have a new ID
            if current_id and current_id != last_processed_id:
                check_nfc_id(current_id)
                last_processed_id = current_id

            time.sleep(0.1)  # Small delay to prevent CPU overuse

    # Start both NFC reader and processor threads
    nfc_thread = threading.Thread(target=read_nfc, daemon=True)
    processor_thread = threading.Thread(target=nfc_processor, daemon=True)

    nfc_thread.start()
    processor_thread.start()


# API endpoints
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
        cursor = conn.cursor()
        rows = cursor.execute("""
                              SELECT name, time
                              FROM users
                              WHERE datetime(created_at) >= datetime('now', '-1 hour')
                              ORDER BY time
                              """).fetchall()
        return [dict(row) for row in rows]

@app.get("/api/leaderAll")
async def get_all_leaders():
    with db.get_connection() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("""
                              SELECT name, time
                              FROM users
                              ORDER BY time
                              """).fetchall()
        return [dict(row) for row in rows]

@app.post("/api/name")
async def check_name(user: NameCheck):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        row = cursor.execute(
            "SELECT name FROM users WHERE name = ?",
            (user.name,)
        ).fetchone()

        if row:
            raise HTTPException(
                status_code=400,
                detail="Name ist bereits vergeben"
            )
        return {"success": True, "message": "Verfügbar!"}

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