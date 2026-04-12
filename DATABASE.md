# Database — Doctor Appointment System (SQLite)

## Tech Stack
- Python built-in sqlite3
- Database file: `data/appointments.db` (auto-created on first run)

---

## How Tables Are Created
```bash
python database.py    # creates all tables with correct schema
```

---

## All Tables

---

### 1. users
```sql
-- Stores all user accounts for all three roles
CREATE TABLE IF NOT EXISTS users (
    user_id     TEXT PRIMARY KEY,   -- UUID generated on signup
    username    TEXT UNIQUE NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,    -- bcrypt hash — never plain text
    role        TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'patient')),
    created_at  TEXT NOT NULL       -- ISO timestamp
);
```

---

### 2. doctors
```sql
-- Stores doctor profiles managed by admin
-- consultation_mode is EITHER Online OR Offline — never both (strict rule)
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
```

---

### 3. shifts
```sql
-- Stores duty shifts created by admin for each doctor
-- mode must match doctor's consultation_mode (enforced in backend)
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
```

---

### 4. slots
```sql
-- Stores individual time slots generated within a shift
-- token_number is auto-assigned (1, 2, 3...) when admin generates slots
-- status changes from "available" to "booked" when patient books
CREATE TABLE IF NOT EXISTS slots (
    slot_id         TEXT PRIMARY KEY,
    shift_id        TEXT NOT NULL REFERENCES shifts(shift_id),
    token_number    INTEGER NOT NULL,   -- assigned in order: 1, 2, 3...
    slot_start      TEXT NOT NULL,      -- HH:MM
    slot_end        TEXT NOT NULL,      -- HH:MM
    status          TEXT NOT NULL DEFAULT 'available'
                    CHECK(status IN ('available', 'booked'))
);
```

---

### 5. appointments
```sql
-- Stores appointment records created when patient books a slot
-- appointment lifecycle: confirmed → completed / cancelled / no-show
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
```

---

### 6. prescriptions
```sql
-- Stores prescription records added by doctor after consultation
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id         TEXT PRIMARY KEY,
    appointment_id          TEXT NOT NULL REFERENCES appointments(appointment_id),
    diagnosis_notes         TEXT,
    prescribed_medicines    TEXT,
    follow_up_instructions  TEXT,
    created_at              TEXT NOT NULL   -- auto-recorded timestamp
);
```

---

### 7. audit_log
```sql
-- Permanent append-only log of all important system actions
-- Never dropped or cleared — grows continuously
CREATE TABLE IF NOT EXISTS audit_log (
    log_id      TEXT PRIMARY KEY,
    action_type TEXT NOT NULL,  -- doctor_added, shift_created, appointment_booked, etc.
    user_id     TEXT,           -- who performed the action
    description TEXT,           -- plain English description of what happened
    target_id   TEXT,           -- which record was affected
    created_at  TEXT NOT NULL
);
```

---

## Relationships

```
users
  └── doctors (user_id → user_id)
  └── appointments (patient_id → user_id)

doctors
  └── shifts (doctor_id → doctor_id)
  └── appointments (doctor_id → doctor_id)

shifts
  └── slots (shift_id → shift_id)

slots
  └── appointments (slot_id → slot_id)

appointments
  └── prescriptions (appointment_id → appointment_id)
```

---

## Critical: Slot Booking Transaction

```sql
-- This is how we prevent double booking — SQLite transaction
-- Both the slot update AND appointment insert happen together or not at all
BEGIN IMMEDIATE;
    SELECT status FROM slots WHERE slot_id = ?;
    -- If status != "available" → ROLLBACK → return 409
    UPDATE slots SET status = 'booked' WHERE slot_id = ?;
    INSERT INTO appointments (...) VALUES (...);
COMMIT;
```

---

## Key Queries Used by Backend

```sql
-- Admin dashboard: revenue by doctor
SELECT d.name, SUM(d.consultation_fee) as revenue
FROM appointments a
JOIN doctors d ON a.doctor_id = d.doctor_id
WHERE a.status = 'completed'
GROUP BY d.doctor_id;

-- Admin dashboard: online vs offline count
SELECT mode, COUNT(*) as count
FROM appointments
GROUP BY mode;

-- Admin dashboard: completion rate
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed
FROM appointments;

-- Patient upcoming appointments
SELECT * FROM appointments
WHERE patient_id = ? AND status = 'confirmed';

-- Available slots for a doctor on a date
SELECT s.* FROM slots s
JOIN shifts sh ON s.shift_id = sh.shift_id
WHERE sh.doctor_id = ? AND sh.date = ? AND s.status = 'available';

-- Doctor appointments with patient names and token numbers
SELECT a.*, u.username as patient_name, a.token_number
FROM appointments a
JOIN users u ON a.patient_id = u.user_id
WHERE a.doctor_id = ?;

-- Patient prescription history
SELECT p.* FROM prescriptions p
JOIN appointments a ON p.appointment_id = a.appointment_id
WHERE a.patient_id = ?;

-- Audit log newest first
SELECT * FROM audit_log ORDER BY created_at DESC;
```

---

## Database Behavior Rules

- All tables created with `CREATE TABLE IF NOT EXISTS` — idempotent, safe to run multiple times
- `audit_log` is append-only — never drop, never clear
- `users` table is append-only — never drop or clear existing users
- `slots` status changes from "available" to "booked" atomically inside a transaction
- All timestamps stored as ISO 8601 strings: `datetime.now().isoformat()`
- All IDs are UUIDs: `str(uuid.uuid4())`
