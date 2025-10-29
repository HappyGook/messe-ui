from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from db import db



app = FastAPI()

buzzer_clicked = False

statuses = {
    "local": None,
    "stl1": None,
    "stl2": None,
    "stl3": None,
    "stl4": None
}

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/api/buzzer")
async def get_buzzer_status():
    global buzzer_clicked
    state = buzzer_clicked
    if buzzer_clicked:
        buzzer_clicked = False  # reset flag immediately
    return {"clicked": state}

@app.get("/api/statuses")
async def get_statuses():
    return statuses

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