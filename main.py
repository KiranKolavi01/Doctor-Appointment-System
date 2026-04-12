import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Any
from fastapi import FastAPI, Header, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from database import get_db_connection
from auth import router as auth_router
from models import (
    DoctorCreate, DoctorUpdate, ShiftCreate, SlotGenerate,
    StatusUpdate, PrescriptionCreate, VideoLinkUpdate, AppointmentBook
)

app = FastAPI(title="Doctor Appointment System Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

def clean_response(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: clean_response(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_response(item) for item in data]
    elif data is None:
        return ""
    return data

class CleanJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return super().render(clean_response(content))

def log_action(conn, action_type, user_id, description, target_id):
    conn.execute(
        "INSERT INTO audit_log (log_id, action_type, user_id, description, target_id, created_at) VALUES (?,?,?,?,?,?)",
        (str(uuid.uuid4()), action_type, user_id, description, target_id, datetime.now().isoformat())
    )

def require_auth(x_user_id: str = Header(...), x_user_role: str = Header(...)):
    if not x_user_id or not x_user_role:
        raise HTTPException(status_code=401, detail="Missing auth headers")
    return {"user_id": x_user_id, "role": x_user_role}

def require_admin(auth: dict = Depends(require_auth)):
    if auth["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return auth

def require_doctor(auth: dict = Depends(require_auth)):
    if auth["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Doctor role required")
    return auth

def require_patient(auth: dict = Depends(require_auth)):
    if auth["role"] != "patient":
        raise HTTPException(status_code=403, detail="Patient role required")
    return auth

# --- ADMIN ENDPOINTS ---

@app.post("/admin/doctors", response_class=CleanJSONResponse)
def add_doctor(req: DoctorCreate, auth: dict = Depends(require_admin)):
    conn = get_db_connection()
    doc_id = str(uuid.uuid4())
    try:
        conn.execute("""
        INSERT INTO doctors (doctor_id, name, speciality, consultation_mode, consultation_fee, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, 1, ?)
        """, (doc_id, req.name, req.speciality, req.consultation_mode.value, req.consultation_fee, datetime.now().isoformat()))
        log_action(conn, "doctor_added", auth["user_id"], f"Added doctor {req.name}", doc_id)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
        
    return {
        "doctor_id": doc_id, "name": req.name, "speciality": req.speciality,
        "consultation_mode": req.consultation_mode.value, "consultation_fee": req.consultation_fee, "is_active": True
    }

@app.put("/admin/doctors/{doctor_id}", response_class=CleanJSONResponse)
def update_doctor(doctor_id: str, req: DoctorUpdate, auth: dict = Depends(require_admin)):
    conn = get_db_connection()
    try:
        conn.execute("""
        UPDATE doctors SET name=?, speciality=?, consultation_mode=?, consultation_fee=?, is_active=?
        WHERE doctor_id=?
        """, (req.name, req.speciality, req.consultation_mode.value, req.consultation_fee, req.is_active, doctor_id))
        if conn.execute("SELECT changes()").fetchone()[0] == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Doctor not found")
            
        log_action(conn, "doctor_updated", auth["user_id"], f"Updated doctor {doctor_id}", doctor_id)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    
    return {
        "doctor_id": doctor_id, "name": req.name, "speciality": req.speciality,
        "consultation_mode": req.consultation_mode.value, "consultation_fee": req.consultation_fee, "is_active": req.is_active
    }

@app.get("/admin/doctors", response_class=CleanJSONResponse)
def get_all_doctors(auth: dict = Depends(require_admin)):
    conn = get_db_connection()
    docs = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()
    return [dict(d) for d in docs]

@app.post("/admin/shifts", response_class=CleanJSONResponse)
def create_shift(req: ShiftCreate, auth: dict = Depends(require_admin)):
    # Business logic validation before DB
    st = datetime.strptime(req.start_time, "%H:%M")
    et = datetime.strptime(req.end_time, "%H:%M")
    if et <= st:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    conn = get_db_connection()
    doc = conn.execute("SELECT consultation_mode, is_active FROM doctors WHERE doctor_id=?", (req.doctor_id,)).fetchone()
    if not doc:
        conn.close()
        raise HTTPException(status_code=404, detail="Doctor not found")
    if doc["is_active"] == 0:
        conn.close()
        raise HTTPException(status_code=400, detail="Doctor is not active")
    if doc["consultation_mode"] != req.mode.value:
        conn.close()
        raise HTTPException(status_code=400, detail="Mode does not match doctor consultation_mode")

    shift_id = str(uuid.uuid4())
    try:
        conn.execute("""
        INSERT INTO shifts (shift_id, doctor_id, date, start_time, end_time, shift_type, mode, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (shift_id, req.doctor_id, req.date, req.start_time, req.end_time, req.shift_type.value, req.mode.value, datetime.now().isoformat()))
        log_action(conn, "shift_created", auth["user_id"], f"Created shift {shift_id}", shift_id)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
        
    return {
        "shift_id": shift_id, "doctor_id": req.doctor_id, "date": req.date,
        "start_time": req.start_time, "end_time": req.end_time, "shift_type": req.shift_type.value, "mode": req.mode.value
    }

@app.get("/admin/shifts", response_class=CleanJSONResponse)
def get_shifts(doctor_id: Optional[str] = None, date: Optional[str] = None, auth: dict = Depends(require_admin)):
    conn = get_db_connection()
    query = "SELECT * FROM shifts WHERE 1=1"
    params = []
    if doctor_id:
        query += " AND doctor_id = ?"
        params.append(doctor_id)
    if date:
        query += " AND date = ?"
        params.append(date)
    shifts = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(s) for s in shifts]

@app.post("/admin/slots", response_class=CleanJSONResponse)
def generate_slots(req: SlotGenerate, auth: dict = Depends(require_admin)):
    conn = get_db_connection()
    shift = conn.execute("SELECT start_time, end_time FROM shifts WHERE shift_id=?", (req.shift_id,)).fetchone()
    if not shift:
        conn.close()
        raise HTTPException(status_code=404, detail="Shift not found")
        
    st = datetime.strptime(shift["start_time"], "%H:%M")
    et = datetime.strptime(shift["end_time"], "%H:%M")
    duration = timedelta(minutes=req.slot_duration_minutes)
    
    current = st
    token = 1
    slots = []
    try:
        while current + duration <= et:
            slot_id = str(uuid.uuid4())
            slot_start = current.strftime("%H:%M")
            slot_end = (current + duration).strftime("%H:%M")
            conn.execute("""
            INSERT INTO slots (slot_id, shift_id, token_number, slot_start, slot_end, status)
            VALUES (?, ?, ?, ?, ?, 'available')
            """, (slot_id, req.shift_id, token, slot_start, slot_end))
            slots.append({
                "slot_id": slot_id, "shift_id": req.shift_id, "token_number": token,
                "slot_start": slot_start, "slot_end": slot_end, "status": "available"
            })
            current += duration
            token += 1
        log_action(conn, "slots_generated", auth["user_id"], f"Generated slots for {req.shift_id}", req.shift_id)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
        
    return slots

@app.get("/admin/slots/{shift_id}", response_class=CleanJSONResponse)
def get_slots_for_shift(shift_id: str, auth: dict = Depends(require_admin)):
    conn = get_db_connection()
    res = conn.execute("SELECT token_number, slot_start, slot_end, status FROM slots WHERE shift_id=?", (shift_id,)).fetchall()
    conn.close()
    return [dict(r) for r in res]

@app.get("/admin/appointments", response_class=CleanJSONResponse)
def get_all_appointments(date: Optional[str] = None, doctor_id: Optional[str] = None, status: Optional[str] = None, auth: dict = Depends(require_admin)):
    conn = get_db_connection()
    query = "SELECT a.* FROM appointments a JOIN slots s ON a.slot_id = s.slot_id JOIN shifts sh ON s.shift_id = sh.shift_id WHERE 1=1"
    params = []
    if date:
        query += " AND sh.date = ?"
        params.append(date)
    if doctor_id:
        query += " AND a.doctor_id = ?"
        params.append(doctor_id)
    if status:
        query += " AND a.status = ?"
        params.append(status)
    res = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in res]

@app.get("/admin/dashboard", response_class=CleanJSONResponse)
def dashboard(auth: dict = Depends(require_admin)):
    conn = get_db_connection()
    today_dt = datetime.now()
    today = today_dt.strftime("%Y-%m-%d")
    
    # Calculate times manually based on sqlite records or pull all and aggregate
    apps = conn.execute("""
    SELECT a.*, sh.date, d.consultation_fee, d.speciality
    FROM appointments a
    JOIN slots s ON a.slot_id = s.slot_id
    JOIN shifts sh ON s.shift_id = sh.shift_id
    JOIN doctors d ON a.doctor_id = d.doctor_id
    """).fetchall()
    
    tot_dy, tot_wk, tot_mo = 0, 0, 0
    rev_by_doc = {}
    rev_by_spec = {}
    onl, off = 0, 0
    completed_qty = 0
    
    for a in apps:
        dt = datetime.strptime(a["date"], "%Y-%m-%d")
        diff = (today_dt - dt).days
        if diff == 0: tot_dy += 1
        if 0 <= diff <= 7: tot_wk += 1
        if 0 <= diff <= 30: tot_mo += 1
        
        if a["status"] == "completed":
            completed_qty += 1
            rev_by_doc[a["doctor_id"]] = rev_by_doc.get(a["doctor_id"], 0) + a["consultation_fee"]
            rev_by_spec[a["speciality"]] = rev_by_spec.get(a["speciality"], 0) + a["consultation_fee"]
            
        if a["mode"] == "Online": onl += 1
        if a["mode"] == "Offline": off += 1
        
    conn.close()
    
    comp_rt = 0
    if len(apps) > 0:
        comp_rt = (completed_qty / len(apps)) * 100
        
    return {
        "total_daily": tot_dy, "total_weekly": tot_wk, "total_monthly": tot_mo,
        "revenue_by_doctor": rev_by_doc, "revenue_by_speciality": rev_by_spec,
        "online_count": onl, "offline_count": off, "completion_rate": comp_rt
    }

@app.get("/admin/patients", response_class=CleanJSONResponse)
def get_patients(auth: dict = Depends(require_admin)):
    conn = get_db_connection()
    res = conn.execute("""
    SELECT u.user_id, u.username, u.email, COUNT(a.appointment_id) as appointment_history_count
    FROM users u LEFT JOIN appointments a ON u.user_id = a.patient_id
    WHERE u.role = 'patient'
    GROUP BY u.user_id
    """).fetchall()
    conn.close()
    return [dict(r) for r in res]

@app.get("/admin/audit-log", response_class=CleanJSONResponse)
def get_audit_log(auth: dict = Depends(require_admin)):
    conn = get_db_connection()
    res = conn.execute("SELECT * FROM audit_log ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in res]

# --- DOCTOR ENDPOINTS ---

@app.get("/doctor/schedule/{doctor_id}", response_class=CleanJSONResponse)
def get_schedule(doctor_id: str, auth: dict = Depends(require_doctor)):
    conn = get_db_connection()
    res = conn.execute("SELECT * FROM shifts WHERE doctor_id = ?", (doctor_id,)).fetchall()
    conn.close()
    return [dict(r) for r in res]

@app.get("/doctor/appointments/{doctor_id}", response_class=CleanJSONResponse)
def get_doctor_appointments(doctor_id: str, auth: dict = Depends(require_doctor)):
    conn = get_db_connection()
    res = conn.execute("""
    SELECT a.appointment_id, u.username as patient_name, a.token_number, s.slot_start, s.slot_end, a.status 
    FROM appointments a
    JOIN users u ON a.patient_id = u.user_id
    JOIN slots s ON a.slot_id = s.slot_id
    WHERE a.doctor_id = ?
    """, (doctor_id,)).fetchall()
    conn.close()
    return [dict(r) for r in res]

@app.get("/doctor/patient-history/{patient_id}", response_class=CleanJSONResponse)
def get_patient_history(patient_id: str, auth: dict = Depends(require_doctor)):
    conn = get_db_connection()
    res = conn.execute("SELECT * FROM appointments WHERE patient_id = ?", (patient_id,)).fetchall()
    raw_apps = [dict(r) for r in res]
    for a in raw_apps:
        pres = conn.execute("SELECT * FROM prescriptions WHERE appointment_id = ?", (a["appointment_id"],)).fetchall()
        a["prescriptions"] = [dict(p) for p in pres]
    conn.close()
    return raw_apps

@app.put("/doctor/appointments/{appointment_id}/status", response_class=CleanJSONResponse)
def update_app_status(appointment_id: str, req: StatusUpdate, auth: dict = Depends(require_doctor)):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE appointments SET status=?, updated_at=? WHERE appointment_id=?", 
                     (req.status.value, datetime.now().isoformat(), appointment_id))
        if conn.execute("SELECT changes()").fetchone()[0] == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Appointment not found")
        log_action(conn, "status_updated", auth["user_id"], f"Updated status of {appointment_id} to {req.status.value}", appointment_id)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
        
    return {"appointment_id": appointment_id, "status": req.status.value}

@app.post("/doctor/prescriptions", response_class=CleanJSONResponse)
def add_prescription(req: PrescriptionCreate, auth: dict = Depends(require_doctor)):
    conn = get_db_connection()
    pres_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    try:
        conn.execute("""
        INSERT INTO prescriptions (prescription_id, appointment_id, diagnosis_notes, prescribed_medicines, follow_up_instructions, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (pres_id, req.appointment_id, req.diagnosis_notes, req.prescribed_medicines, req.follow_up_instructions, now))
        log_action(conn, "prescription_added", auth["user_id"], f"Added prescription for {req.appointment_id}", pres_id)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
        
    return {"prescription_id": pres_id, "appointment_id": req.appointment_id, "created_at": now}

@app.put("/doctor/appointments/{appointment_id}/video-link", response_class=CleanJSONResponse)
def add_video_link(appointment_id: str, req: VideoLinkUpdate, auth: dict = Depends(require_doctor)):
    conn = get_db_connection()
    app_record = conn.execute("SELECT mode FROM appointments WHERE appointment_id=?", (appointment_id,)).fetchone()
    if not app_record:
        conn.close()
        raise HTTPException(status_code=404, detail="Appointment not found")
    if app_record["mode"] != "Online":
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot add video link to Offline appointment")
        
    try:
        conn.execute("UPDATE appointments SET video_link=?, updated_at=? WHERE appointment_id=?", 
                     (req.video_link, datetime.now().isoformat(), appointment_id))
        log_action(conn, "video_link_added", auth["user_id"], f"Added video link to {appointment_id}", appointment_id)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
        
    return {"appointment_id": appointment_id, "video_link": req.video_link}

# --- PATIENT ENDPOINTS ---

@app.get("/patient/doctors", response_class=CleanJSONResponse)
def search_doctors(speciality: Optional[str] = None, mode: Optional[str] = None, available: Optional[bool] = None, auth: dict = Depends(require_patient)):
    conn = get_db_connection()
    query = "SELECT * FROM doctors WHERE is_active=1"
    params = []
    if speciality:
        query += " AND speciality = ?"
        params.append(speciality)
    if mode:
        query += " AND consultation_mode = ?"
        params.append(mode)
        
    docs = conn.execute(query, params).fetchall()
    
    # If available is true, we should probably check if they have available slots
    res = [dict(d) for d in docs]
    if available:
        filtered = []
        for d in res:
            slots = conn.execute("""
            SELECT COUNT(slot_id) FROM slots s
            JOIN shifts sh ON s.shift_id = sh.shift_id
            WHERE sh.doctor_id = ? AND s.status = 'available'
            """, (d["doctor_id"],)).fetchone()
            if slots[0] > 0:
                filtered.append(d)
        res = filtered
        
    conn.close()
    return res

@app.get("/patient/slots", response_class=CleanJSONResponse)
def get_available_slots(doctor_id: str, date: Optional[str] = None, auth: dict = Depends(require_patient)):
    conn = get_db_connection()
    query = """
    SELECT s.* FROM slots s
    JOIN shifts sh ON s.shift_id = sh.shift_id
    WHERE sh.doctor_id = ? AND s.status = 'available'
    """
    params = [doctor_id]
    if date:
        query += " AND sh.date = ?"
        params.append(date)
        
    res = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in res]

@app.post("/patient/appointments", response_class=CleanJSONResponse)
def book_appointment(req: AppointmentBook, auth: dict = Depends(require_patient)):
    conn = get_db_connection()
    app_id = str(uuid.uuid4())
    try:
        conn.execute("BEGIN IMMEDIATE")
        
        slot = conn.execute("""
        SELECT s.status, s.token_number, s.slot_start, sh.doctor_id, sh.mode, d.name 
        FROM slots s
        JOIN shifts sh ON s.shift_id = sh.shift_id
        JOIN doctors d ON sh.doctor_id = d.doctor_id
        WHERE s.slot_id = ?
        """, (req.slot_id,)).fetchone()
        
        if not slot:
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=404, detail="Slot not found")
            
        if slot["status"] != "available":
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=409, detail="Slot implicitly booked")
            
        conn.execute("UPDATE slots SET status = 'booked' WHERE slot_id = ?", (req.slot_id,))
        
        conn.execute("""
        INSERT INTO appointments (appointment_id, patient_id, doctor_id, slot_id, token_number, status, mode, created_at)
        VALUES (?, ?, ?, ?, ?, 'confirmed', ?, ?)
        """, (app_id, req.patient_id, slot["doctor_id"], req.slot_id, slot["token_number"], slot["mode"], datetime.now().isoformat()))
        
        log_action(conn, "appointment_booked", auth["user_id"], f"Patient booked slot {req.slot_id}", app_id)
        conn.commit()
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
        
    return {
        "appointment_id": app_id, 
        "token_number": slot["token_number"], 
        "slot_start": slot["slot_start"], 
        "doctor_name": slot["name"], 
        "mode": slot["mode"]
    }

@app.get("/patient/appointments/{patient_id}", response_class=CleanJSONResponse)
def get_patient_appointments(patient_id: str, auth: dict = Depends(require_patient)):
    if patient_id != auth["user_id"]:
        raise HTTPException(status_code=403, detail="Can only view your own appointments")
        
    conn = get_db_connection()
    res = conn.execute("SELECT * FROM appointments WHERE patient_id = ?", (patient_id,)).fetchall()
    conn.close()
    
    upcoming = []
    past = []
    for r in res:
        d = dict(r)
        if d["status"] == "confirmed":
            upcoming.append(d)
        else:
            past.append(d)
            
    return {"upcoming": upcoming, "past": past}

@app.get("/patient/prescriptions/{patient_id}", response_class=CleanJSONResponse)
def get_patient_prescriptions(patient_id: str, auth: dict = Depends(require_patient)):
    if patient_id != auth["user_id"]:
        raise HTTPException(status_code=403, detail="Can only view your own prescriptions")
        
    conn = get_db_connection()
    res = conn.execute("""
    SELECT p.* FROM prescriptions p
    JOIN appointments a ON p.appointment_id = a.appointment_id
    WHERE a.patient_id = ?
    """, (patient_id,)).fetchall()
    conn.close()
    return [dict(r) for r in res]

@app.get("/patient/appointment/{appointment_id}/video-link", response_class=CleanJSONResponse)
def get_app_video_link(appointment_id: str, auth: dict = Depends(require_patient)):
    conn = get_db_connection()
    rec = conn.execute("SELECT patient_id, video_link FROM appointments WHERE appointment_id=?", (appointment_id,)).fetchone()
    conn.close()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    if rec["patient_id"] != auth["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this appointment")
        
    return {"video_link": rec["video_link"]}

@app.get("/patient/appointment/{appointment_id}/clinic-info", response_class=CleanJSONResponse)
def get_app_clinic_info(appointment_id: str, auth: dict = Depends(require_patient)):
    conn = get_db_connection()
    rec = conn.execute("""
    SELECT a.patient_id, a.mode, d.clinic_address, sh.date as shift_date, sh.start_time, sh.end_time 
    FROM appointments a
    JOIN doctors d ON a.doctor_id = d.doctor_id
    JOIN slots s ON a.slot_id = s.slot_id
    JOIN shifts sh ON s.shift_id = sh.shift_id
    WHERE a.appointment_id=?
    """, (appointment_id,)).fetchone()
    conn.close()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    if rec["patient_id"] != auth["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this appointment")
        
    if rec["mode"] != "Offline":
        raise HTTPException(status_code=400, detail="Cannot get clinic info for Online appointment")
        
    return {
        "clinic_address": rec["clinic_address"],
        "shift_date": rec["shift_date"],
        "start_time": rec["start_time"],
        "end_time": rec["end_time"]
    }
