import bcrypt
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from database import get_db_connection
from models import SignupRequest, SigninRequest

router = APIRouter(prefix="/auth")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@router.post("/signup")
def signup(req: SignupRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Validate unique username
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (req.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
        
    # Validate unique email
    cursor.execute("SELECT user_id FROM users WHERE email = ?", (req.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already exists")
        
    user_id = str(uuid.uuid4())
    hashed_pw = hash_password(req.password)
    
    cursor.execute("""
    INSERT INTO users (user_id, username, email, password_hash, role, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, req.username, req.email, hashed_pw, req.role.value, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "user_id": user_id}

@router.post("/signin")
def signin(req: SigninRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, username, password_hash, role FROM users WHERE username = ?", (req.username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=401, detail="Wrong credentials")
        
    if not verify_password(req.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Wrong credentials")
        
    return {
        "status": "success",
        "username": row["username"],
        "role": row["role"],
        "user_id": row["user_id"]
    }
