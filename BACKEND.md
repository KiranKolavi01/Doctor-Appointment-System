# Backend — Doctor Appointment System (FastAPI)

## Tech Stack
- Python 3.10+
- FastAPI
- SQLite (built-in sqlite3)
- bcrypt
- pandas
- uvicorn

---

## How to Run
```bash
python database.py      # creates all tables first
uvicorn main:app --reload
# Runs at http://127.0.0.1:8000
# Swagger docs at http://127.0.0.1:8000/docs
```

---

## Project Structure
```
project/
├── main.py          # FastAPI app — all routes registered here
├── database.py      # SQLite connection and table creation
├── auth.py          # Signup, signin, bcrypt password hashing
├── models.py        # Pydantic models for input validation
├── requirements.txt
└── data/
    └── appointments.db   # SQLite database (auto-created)
```

---

## Data Flow — The Pipeline
```
HTTP Request
    ↓
Role Check (admin / doctor / patient)
    ↓
Input Validation (Pydantic models)
    ↓
Business Rule Check (mode match, slot available, role permissions)
    ↓
SQLite Read / Write (with transaction lock for slot booking)
    ↓
JSON Response
```

---

## Three User Roles — Strict Separation
- Admin — full control: doctors, shifts, slots, reports, audit
- Doctor — read-only schedule, update appointment status, add prescription, add video link
- Patient — browse doctors, filter, book slots, view history

---

## CRITICAL BUSINESS RULES — Enforced at Every Relevant Endpoint

```python
# RULE 1: Online and Offline consultations must use DIFFERENT doctors
# Each doctor is assigned EITHER Online OR Offline at creation — never both
# When a shift is created, its mode must match the doctor's consultation_mode

# RULE 2: Double booking prevented using SQLite transactional locking
# BEGIN IMMEDIATE locks the slot row
# Check status = "available" inside transaction
# Update to "booked" inside same transaction
# COMMIT only if slot was available — else ROLLBACK and return HTTP 409

# RULE 3: Doctors CANNOT create, edit, or delete slots — Admin only

# RULE 4: Video link visible ONLY to the booked patient for that appointment

# RULE 5: Shift mode must match doctor's consultation_mode — validated at shift creation
```

---

## Authentication

### POST /auth/signup
```
# Creates new user with bcrypt hashed password — never store plain text
Body: { username, email, password, role }
Role must be: admin / doctor / patient
Validates: username unique, email unique, password min 8 chars
Returns: { status: "success", user_id }
HTTP 400 if username or email already exists
```

### POST /auth/signin
```
# Checks credentials and returns user role for session management
Body: { username, password }
Validates: username exists, bcrypt.checkpw() matches stored hash
Returns: { status: "success", username, role, user_id }
HTTP 401 if wrong credentials
```

---

## Admin Endpoints

### POST /admin/doctors
```
# Adds a new doctor — mode is permanently Online OR Offline
Body: { name, speciality, consultation_mode, consultation_fee }
consultation_mode: "Online" OR "Offline" only
consultation_fee: must be positive number
Returns: { doctor_id, name, speciality, consultation_mode, consultation_fee, is_active: true }
```

### PUT /admin/doctors/{doctor_id}
```
# Updates doctor info or deactivates a doctor
Body: { name, speciality, consultation_mode, consultation_fee, is_active }
Returns: updated doctor record
```

### GET /admin/doctors
```
# Returns all doctors in the system
Returns: list of all doctor records
```

### POST /admin/shifts
```
# Admin creates a duty shift for a doctor on a specific date
Body: { doctor_id, date, start_time, end_time, shift_type, mode }
shift_type: "Morning" / "Evening" / "Night"
mode: must match the doctor's consultation_mode — HTTP 400 if mismatch
Validates: end_time after start_time, doctor must be active
Returns: { shift_id, doctor_id, date, start_time, end_time, shift_type, mode }
```

### GET /admin/shifts
```
# Returns all shifts — filterable by doctor or date
Query params: doctor_id (optional), date (optional)
Returns: list of shift records
```

### POST /admin/slots
```
# Generates time-based slots inside a shift with token numbers auto-assigned
Body: { shift_id, slot_duration_minutes }
slot_duration_minutes: 15 / 20 / 30 only
Auto-calculates slots from shift start_time to end_time
Auto-assigns token_number: 1, 2, 3... for each slot
Sets each slot status to "available"
Returns: list of generated slot records with token numbers

# Slot generation logic:
current = shift.start_time
token = 1
while current + duration <= shift.end_time:
    create slot(token, current, current+duration, "available")
    current += duration
    token += 1
```

### GET /admin/slots/{shift_id}
```
# Returns all slots for a shift with their booking status
Returns: list of slots (token_number, start_time, end_time, status)
```

### GET /admin/appointments
```
# Returns all appointments across all doctors for monitoring
Query params: date (optional), doctor_id (optional), status (optional)
Returns: list of all appointment records
```

### GET /admin/dashboard
```
# Calculates and returns all dashboard metrics for admin overview
Calculates:
  - Total appointments grouped by daily / weekly / monthly
  - Revenue per doctor (sum of consultation_fee for completed appointments)
  - Revenue per speciality
  - Online vs Offline count
  - Completion rate = completed / total * 100
Returns: { total_daily, total_weekly, total_monthly, revenue_by_doctor,
           revenue_by_speciality, online_count, offline_count, completion_rate }
```

### GET /admin/patients
```
# Returns all patient profiles with appointment history count
Returns: list of patient records with appointment counts
```

### GET /admin/audit-log
```
# Returns audit log of all system actions ordered newest first
Returns: list of audit entries (action_type, user_id, description, created_at)
```

---

## Doctor Endpoints

### GET /doctor/schedule/{doctor_id}
```
# Returns the doctor's weekly shift schedule — read only
Returns: list of shifts for this doctor for the current week
```

### GET /doctor/appointments/{doctor_id}
```
# Returns all booked appointments for this doctor with patient info and token numbers
Returns: list of { appointment_id, patient_name, token_number, slot_start, slot_end, status }
```

### GET /doctor/patient-history/{patient_id}
```
# Returns full past appointment and prescription history for a specific patient
Returns: list of past appointments with their prescriptions
```

### PUT /doctor/appointments/{appointment_id}/status
```
# Doctor updates appointment status after consultation
Body: { status }
status must be one of: "confirmed" / "completed" / "cancelled" / "no-show"
Auto-records updated_at timestamp
Returns: updated appointment record
HTTP 400 if invalid status value
```

### POST /doctor/prescriptions
```
# Doctor adds prescription after completing a consultation
Body: { appointment_id, diagnosis_notes, prescribed_medicines, follow_up_instructions }
appointment_id is required — all other fields optional
Auto-records created_at timestamp
Returns: { prescription_id, appointment_id, created_at }
```

### PUT /doctor/appointments/{appointment_id}/video-link
```
# Doctor adds video consultation link — for Online appointments only
Body: { video_link }
Validates: appointment must be for Online mode doctor — HTTP 400 if Offline
Link stored — visible only to booked patient (enforced in patient endpoint)
Returns: { appointment_id, video_link }
```

---

## Patient Endpoints

### GET /patient/doctors
```
# Returns list of active doctors — patient filters by speciality, mode, or availability
Query params: speciality (optional), mode (optional), available (optional boolean)
Returns: filtered list of active doctors
```

### GET /patient/slots
```
# Returns only available (not booked) slots for a doctor on a date
Query params: doctor_id (required), date (optional)
Returns: only slots where status = "available"
```

### POST /patient/appointments
```
# Patient books a slot — slot locked immediately using SQLite transaction
Body: { patient_id, slot_id }
TRANSACTION FLOW:
  BEGIN IMMEDIATE         ← locks the slot row
  SELECT status WHERE slot_id = ?   ← check inside transaction
  IF status != "available" → ROLLBACK → HTTP 409 Conflict
  UPDATE slots SET status = "booked"
  INSERT INTO appointments (status="confirmed", token from slot)
  COMMIT
Returns: { appointment_id, token_number, slot_start, doctor_name, mode }
HTTP 409 if slot already booked
```

### GET /patient/appointments/{patient_id}
```
# Returns all appointments for this patient split into upcoming and past
Returns: {
  upcoming: [ appointments with status="confirmed" ],
  past: [ appointments with status="completed"/"cancelled"/"no-show" ]
}
```

### GET /patient/prescriptions/{patient_id}
```
# Returns all prescriptions for this patient across all appointments
Returns: list of prescriptions with diagnosis, medicines, follow-up
```

### GET /patient/appointment/{appointment_id}/video-link
```
# Returns video link — validates that requesting patient is the booked patient
Validates: patient_id must match appointment.patient_id
Returns: { video_link }
HTTP 403 if patient_id does not match
```

### GET /patient/appointment/{appointment_id}/clinic-info
```
# Returns clinic address and shift timing for offline appointments
Validates: appointment must be Offline mode
Returns: { clinic_address, shift_date, start_time, end_time }
HTTP 400 if appointment is Online mode
```

---

## Audit Logging — All Important Actions Logged

```python
# Every important action writes to audit_log table
# Actions logged:
#   doctor_added, shift_created, slots_generated, appointment_booked,
#   status_updated, prescription_added, video_link_added

def log_action(conn, action_type, user_id, description, target_id):
    # Inserts one audit row every time a significant action happens
    conn.execute(
        "INSERT INTO audit_log (action_type, user_id, description, target_id, created_at) VALUES (?,?,?,?,?)",
        (action_type, user_id, description, target_id, datetime.now().isoformat())
    )
```

---

## Error Handling

```python
# Every endpoint wrapped in try/except
# Pydantic handles invalid input automatically → HTTP 422
# Business rule violations → HTTP 400 with specific message
# Double booking → HTTP 409
# Wrong role access → HTTP 403
# Record not found → HTTP 404
# All JSON responses: replace None with "" before returning
```

---

## Requirements.txt
```
fastapi
uvicorn[standard]
bcrypt
pandas
pydantic
python-multipart
```
