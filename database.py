import sqlite3
import os

def init_db():
    # Database path
    db_path = os.path.join('data', 'appointments.db')
    
    # Ensure data/ directory exists
    os.makedirs('data', exist_ok=True)
    
    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # SQL Schema from DATABASE.md
    schema = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id     TEXT PRIMARY KEY,   -- UUID generated on signup
            username    TEXT UNIQUE NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,    -- bcrypt hash — never plain text
            role        TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'patient')),
            created_at  TEXT NOT NULL       -- ISO timestamp
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id           TEXT PRIMARY KEY,
            user_id             TEXT,                   -- links to users table
            name                TEXT NOT NULL,
            speciality          TEXT NOT NULL,
            consultation_mode   TEXT NOT NULL CHECK(consultation_mode IN ('Online', 'Offline')),
            consultation_fee    REAL NOT NULL CHECK(consultation_fee >= 0),
            is_active           INTEGER NOT NULL DEFAULT 1,  -- 1=active, 0=deactivated
            clinic_address      TEXT,                   -- used for Offline appointments
            created_at          TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS shifts (
            shift_id    TEXT PRIMARY KEY,
            doctor_id   TEXT NOT NULL REFERENCES doctors(doctor_id),
            date        TEXT NOT NULL,          -- YYYY-MM-DD
            start_time  TEXT NOT NULL,          -- HH:MM
            end_time    TEXT NOT NULL,          -- HH:MM
            shift_type  TEXT NOT NULL CHECK(shift_type IN ('Morning', 'Evening', 'Night')),
            mode        TEXT NOT NULL CHECK(mode IN ('Online', 'Offline')),
            created_at  TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS slots (
            slot_id         TEXT PRIMARY KEY,
            shift_id        TEXT NOT NULL REFERENCES shifts(shift_id),
            token_number    INTEGER NOT NULL,   -- assigned in order: 1, 2, 3...
            slot_start      TEXT NOT NULL,      -- HH:MM
            slot_end        TEXT NOT NULL,      -- HH:MM
            status          TEXT NOT NULL DEFAULT 'available'
                            CHECK(status IN ('available', 'booked'))
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id  TEXT PRIMARY KEY,
            patient_id      TEXT NOT NULL REFERENCES users(user_id),
            doctor_id       TEXT NOT NULL REFERENCES doctors(doctor_id),
            slot_id         TEXT NOT NULL REFERENCES slots(slot_id),
            token_number    INTEGER NOT NULL,   -- copied from slot at booking time
            status          TEXT NOT NULL DEFAULT 'confirmed'
                            CHECK(status IN ('confirmed', 'completed', 'cancelled', 'no-show')),
            mode            TEXT NOT NULL CHECK(mode IN ('Online', 'Offline')),
            video_link      TEXT,               -- set by doctor for Online appointments only
            created_at      TEXT NOT NULL,
            updated_at      TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS prescriptions (
            prescription_id         TEXT PRIMARY KEY,
            appointment_id          TEXT NOT NULL REFERENCES appointments(appointment_id),
            diagnosis_notes         TEXT,
            prescribed_medicines    TEXT,
            follow_up_instructions  TEXT,
            created_at              TEXT NOT NULL   -- auto-recorded timestamp
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id      TEXT PRIMARY KEY,
            action_type TEXT NOT NULL,  -- doctor_added, shift_created, appointment_booked, etc.
            user_id     TEXT,           -- who performed the action
            description TEXT,           -- plain English description of what happened
            target_id   TEXT,           -- which record was affected
            created_at  TEXT NOT NULL
        );
        """
    ]
    
    # Execute ALL CREATE TABLE statements
    for statement in schema:
        cursor.execute(statement)
    
    conn.commit()
    conn.close()
    print("Database and tables created successfully.")

def book_slot_transaction(conn, slot_id, appointment_data):
    """
    Prevent double booking — SQLite transaction
    Both the slot update AND appointment insert happen together or not at all
    """
    cursor = conn.cursor()
    try:
        # BEGIN IMMEDIATE to lock for writing
        cursor.execute("BEGIN IMMEDIATE;")
        
        # SELECT slot status
        cursor.execute("SELECT status FROM slots WHERE slot_id = ?;", (slot_id,))
        result = cursor.fetchone()
        
        if not result or result[0] != 'available':
            cursor.execute("ROLLBACK;")
            return {"success": False, "message": "Slot not available"}
        
        # Else: UPDATE slot
        cursor.execute("UPDATE slots SET status = 'booked' WHERE slot_id = ?;", (slot_id,))
        
        # INSERT appointment
        # appointment_data should be a tuple matching the appointments table columns
        # (appointment_id, patient_id, doctor_id, slot_id, token_number, status, mode, video_link, created_at, updated_at)
        placeholders = ", ".join(["?"] * 10)
        cursor.execute(f"INSERT INTO appointments VALUES ({placeholders});", appointment_data)
        
        # COMMIT
        conn.commit()
        return {"success": True, "message": "Appointment booked successfully"}
        
    except Exception as e:
        # Handle exceptions with rollback
        cursor.execute("ROLLBACK;")
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    init_db()
