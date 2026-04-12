import sqlite3
import os

DB_DIR = "data"
DB_FILE = os.path.join(DB_DIR, "appointments.db")

def get_db_connection():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id     TEXT PRIMARY KEY,
        username    TEXT UNIQUE NOT NULL,
        email       TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role        TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'patient')),
        created_at  TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id           TEXT PRIMARY KEY,
        user_id             TEXT,
        name                TEXT NOT NULL,
        speciality          TEXT NOT NULL,
        consultation_mode   TEXT NOT NULL CHECK(consultation_mode IN ('Online', 'Offline')),
        consultation_fee    REAL NOT NULL CHECK(consultation_fee >= 0),
        is_active           INTEGER NOT NULL DEFAULT 1,
        clinic_address      TEXT,
        created_at          TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shifts (
        shift_id    TEXT PRIMARY KEY,
        doctor_id   TEXT NOT NULL REFERENCES doctors(doctor_id),
        date        TEXT NOT NULL,
        start_time  TEXT NOT NULL,
        end_time    TEXT NOT NULL,
        shift_type  TEXT NOT NULL CHECK(shift_type IN ('Morning', 'Evening', 'Night')),
        mode        TEXT NOT NULL CHECK(mode IN ('Online', 'Offline')),
        created_at  TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS slots (
        slot_id         TEXT PRIMARY KEY,
        shift_id        TEXT NOT NULL REFERENCES shifts(shift_id),
        token_number    INTEGER NOT NULL,
        slot_start      TEXT NOT NULL,
        slot_end        TEXT NOT NULL,
        status          TEXT NOT NULL DEFAULT 'available'
                        CHECK(status IN ('available', 'booked'))
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id  TEXT PRIMARY KEY,
        patient_id      TEXT NOT NULL REFERENCES users(user_id),
        doctor_id       TEXT NOT NULL REFERENCES doctors(doctor_id),
        slot_id         TEXT NOT NULL REFERENCES slots(slot_id),
        token_number    INTEGER NOT NULL,
        status          TEXT NOT NULL DEFAULT 'confirmed'
                        CHECK(status IN ('confirmed', 'completed', 'cancelled', 'no-show')),
        mode            TEXT NOT NULL CHECK(mode IN ('Online', 'Offline')),
        video_link      TEXT,
        created_at      TEXT NOT NULL,
        updated_at      TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        prescription_id         TEXT PRIMARY KEY,
        appointment_id          TEXT NOT NULL REFERENCES appointments(appointment_id),
        diagnosis_notes         TEXT,
        prescribed_medicines    TEXT,
        follow_up_instructions  TEXT,
        created_at              TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        log_id      TEXT PRIMARY KEY,
        action_type TEXT NOT NULL,
        user_id     TEXT,
        description TEXT,
        target_id   TEXT,
        created_at  TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
