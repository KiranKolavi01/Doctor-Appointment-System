# Frontend — Doctor Appointment System (Streamlit + HTML/CSS)

## Tech Stack
- Python
- Streamlit (primary)
- HTML + CSS (minor polishing only — fonts, colors, spacing)

---

## How to Run
```bash
streamlit run app.py
# Opens at http://localhost:8501
```

---

## Auth State + Page Refresh Persistence

```python
# Initialize session state before anything else — prevents KeyError crashes
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = ""
if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

# Read current page from URL on refresh — prevents redirect to default page
params = st.query_params
if "page" in params:
    st.session_state["current_page"] = params["page"]
elif "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

# Navigate and update URL at same time
def navigate_to(page_name):
    st.session_state["current_page"] = page_name
    st.query_params["page"] = page_name

# If not logged in — show only Sign In or Sign Up
if not st.session_state["username"]:
    show_auth_pages()
else:
    show_dashboard_for_role(st.session_state["role"])
```

---

## Sign Up Page

```python
# Shown when user has no account — collects required fields
st.title("Create Account")

username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")     # masked
confirm = st.text_input("Confirm Password", type="password")
role = st.selectbox("Role", ["patient", "doctor", "admin"])

if st.button("Sign Up"):
    # Validate before calling API
    if not all([username, email, password, confirm]):
        st.error("All fields are required")
    elif password != confirm:
        st.error("Passwords do not match")
    elif len(password) < 8:
        st.error("Password must be at least 8 characters")
    else:
        # Call backend signup endpoint
        response = requests.post(f"{API_URL}/auth/signup",
            json={"username": username, "email": email,
                  "password": password, "role": role})
        if response.status_code == 200:
            st.success("Account created. Please Sign In.")
        else:
            st.error(response.json().get("detail", "Signup failed"))

st.write("Already have an account?")
if st.button("Go to Sign In"):
    navigate_to("signin")
```

---

## Sign In Page

```python
# Default landing page when not logged in
st.title("Sign In")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Sign In"):
    if not username or not password:
        st.error("Please enter username and password")
    else:
        response = requests.post(f"{API_URL}/auth/signin",
            json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            # Store role and user info in session
            st.session_state["username"] = data["username"]
            st.session_state["role"] = data["role"]
            st.session_state["user_id"] = data["user_id"]
            navigate_to("dashboard")
            st.rerun()
        else:
            st.error("Invalid username or password")

if st.button("Create Account"):
    navigate_to("signup")
```

---

## Sidebar Navigation

```python
# Sidebar shows different pages based on logged-in role
# Sign Out button always visible when logged in
with st.sidebar:
    st.write(f"Logged in as: {st.session_state['username']}")
    st.write(f"Role: {st.session_state['role']}")

    if st.session_state["role"] == "admin":
        pages = ["Dashboard", "Manage Doctors", "Manage Shifts",
                 "Manage Slots", "All Appointments", "Patient Records", "Audit Log"]
    elif st.session_state["role"] == "doctor":
        pages = ["My Schedule", "My Appointments", "Update Status", "Add Prescription", "Add Video Link"]
    else:  # patient
        pages = ["Browse Doctors", "Book Appointment", "My Appointments", "My Prescriptions"]

    for page in pages:
        # Highlight currently active page
        if st.session_state["current_page"] == page:
            st.markdown(f"**→ {page}**")
        else:
            if st.button(page):
                navigate_to(page)

    if st.button("Sign Out"):
        # Clear session and go back to sign in
        for key in ["username", "role", "user_id", "current_page"]:
            st.session_state[key] = ""
        st.query_params.clear()
        st.rerun()
```

---

## Admin Pages

### Dashboard Page
```python
# Shows summary metrics — total appointments, revenue, online vs offline
st.title("Admin Dashboard")
with st.spinner("Loading dashboard..."):
    response = requests.get(f"{API_URL}/admin/dashboard")
    if response.status_code == 200:
        data = response.json()
        col1, col2, col3 = st.columns(3)
        col1.metric("Today's Appointments", data["total_daily"])
        col2.metric("This Week", data["total_weekly"])
        col3.metric("This Month", data["total_monthly"])

        col4, col5 = st.columns(2)
        col4.metric("Online Appointments", data["online_count"])
        col5.metric("Offline Appointments", data["offline_count"])

        st.metric("Completion Rate", f"{data['completion_rate']:.1f}%")

        # Revenue tables
        st.subheader("Revenue by Doctor")
        st.dataframe(pd.DataFrame(data["revenue_by_doctor"]))
        st.subheader("Revenue by Speciality")
        st.dataframe(pd.DataFrame(data["revenue_by_speciality"]))
    else:
        st.error("Failed to load dashboard data")
```

### Manage Doctors Page
```python
# Add new doctor and view all doctors
st.title("Manage Doctors")

with st.expander("Add New Doctor"):
    name = st.text_input("Doctor Name")
    speciality = st.text_input("Speciality")
    mode = st.selectbox("Consultation Mode", ["Online", "Offline"])
    fee = st.number_input("Consultation Fee", min_value=0.0)
    if st.button("Add Doctor"):
        with st.spinner("Adding..."):
            r = requests.post(f"{API_URL}/admin/doctors",
                json={"name": name, "speciality": speciality,
                      "consultation_mode": mode, "consultation_fee": fee})
            if r.status_code == 200:
                st.success("Doctor added successfully")
            else:
                st.error(r.json().get("detail", "Failed to add doctor"))

# Show all doctors
with st.spinner("Loading doctors..."):
    r = requests.get(f"{API_URL}/admin/doctors")
    if r.status_code == 200:
        df = pd.DataFrame(r.json())
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Failed to load doctors")
```

### Manage Shifts Page
```python
# Admin creates shifts for doctors
st.title("Manage Shifts")

with st.expander("Create New Shift"):
    doctor_id = st.text_input("Doctor ID")
    date = st.date_input("Date")
    shift_type = st.selectbox("Shift Type", ["Morning", "Evening", "Night"])
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    mode = st.selectbox("Mode", ["Online", "Offline"])

    if st.button("Create Shift"):
        with st.spinner("Creating..."):
            r = requests.post(f"{API_URL}/admin/shifts",
                json={"doctor_id": doctor_id, "date": str(date),
                      "start_time": str(start_time), "end_time": str(end_time),
                      "shift_type": shift_type, "mode": mode})
            if r.status_code == 200:
                st.success("Shift created")
            else:
                st.error(r.json().get("detail", "Failed"))

with st.spinner("Loading shifts..."):
    r = requests.get(f"{API_URL}/admin/shifts")
    if r.status_code == 200:
        st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
    else:
        st.error("Failed to load shifts")
```

### Manage Slots Page
```python
# Admin generates time slots for a shift
st.title("Manage Slots")

shift_id = st.text_input("Shift ID")
duration = st.selectbox("Slot Duration (minutes)", [15, 20, 30])

if st.button("Generate Slots"):
    with st.spinner("Generating..."):
        r = requests.post(f"{API_URL}/admin/slots",
            json={"shift_id": shift_id, "slot_duration_minutes": duration})
        if r.status_code == 200:
            st.success(f"Slots generated")
            st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
        else:
            st.error(r.json().get("detail", "Failed"))

if shift_id and st.button("View Slots for This Shift"):
    with st.spinner("Loading..."):
        r = requests.get(f"{API_URL}/admin/slots/{shift_id}")
        if r.status_code == 200:
            st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
        else:
            st.error("Failed to load slots")
```

### All Appointments Page
```python
# Admin monitors all appointments with filters
st.title("All Appointments")

col1, col2, col3 = st.columns(3)
date_filter = col1.text_input("Filter by Date (YYYY-MM-DD)")
doctor_filter = col2.text_input("Filter by Doctor ID")
status_filter = col3.selectbox("Filter by Status",
    ["", "confirmed", "completed", "cancelled", "no-show"])

with st.spinner("Loading..."):
    params = {}
    if date_filter: params["date"] = date_filter
    if doctor_filter: params["doctor_id"] = doctor_filter
    if status_filter: params["status"] = status_filter
    r = requests.get(f"{API_URL}/admin/appointments", params=params)
    if r.status_code == 200:
        df = pd.DataFrame(r.json())
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Failed to load appointments")
```

### Patient Records Page
```python
# Admin views all patient profiles
st.title("Patient Records")
with st.spinner("Loading..."):
    r = requests.get(f"{API_URL}/admin/patients")
    if r.status_code == 200:
        st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
    else:
        st.error("Failed to load patients")
```

### Audit Log Page
```python
# Admin views all system actions
st.title("Audit Log")
with st.spinner("Loading..."):
    r = requests.get(f"{API_URL}/admin/audit-log")
    if r.status_code == 200:
        st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
    else:
        st.error("Failed to load audit log")
```

---

## Doctor Pages

### My Schedule Page
```python
# Doctor sees their weekly shift schedule — read only
st.title("My Weekly Schedule")
with st.spinner("Loading schedule..."):
    r = requests.get(f"{API_URL}/doctor/schedule/{st.session_state['user_id']}")
    if r.status_code == 200:
        st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
    else:
        st.error("Failed to load schedule")
```

### My Appointments Page
```python
# Doctor sees all booked appointments with patient info and token numbers
st.title("My Appointments")
with st.spinner("Loading..."):
    r = requests.get(f"{API_URL}/doctor/appointments/{st.session_state['user_id']}")
    if r.status_code == 200:
        st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
    else:
        st.error("Failed to load appointments")
```

### Update Status Page
```python
# Doctor updates appointment status after consultation
st.title("Update Appointment Status")
appointment_id = st.text_input("Appointment ID")
new_status = st.selectbox("New Status", ["confirmed", "completed", "cancelled", "no-show"])

if st.button("Update"):
    with st.spinner("Updating..."):
        r = requests.put(f"{API_URL}/doctor/appointments/{appointment_id}/status",
            json={"status": new_status})
        if r.status_code == 200:
            st.success("Status updated")
        else:
            st.error(r.json().get("detail", "Failed to update"))
```

### Add Prescription Page
```python
# Doctor adds prescription for a completed appointment
st.title("Add Prescription")
appt_id = st.text_input("Appointment ID")
diagnosis = st.text_area("Diagnosis Notes")
medicines = st.text_area("Prescribed Medicines")
follow_up = st.text_area("Follow-up Instructions")

if st.button("Save Prescription"):
    with st.spinner("Saving..."):
        r = requests.post(f"{API_URL}/doctor/prescriptions",
            json={"appointment_id": appt_id, "diagnosis_notes": diagnosis,
                  "prescribed_medicines": medicines, "follow_up_instructions": follow_up})
        if r.status_code == 200:
            st.success("Prescription saved")
        else:
            st.error(r.json().get("detail", "Failed"))
```

### Add Video Link Page
```python
# Doctor adds video link for online appointments only
st.title("Add Video Consultation Link")
appt_id = st.text_input("Appointment ID")
video_link = st.text_input("Video Link URL")

if st.button("Save Link"):
    with st.spinner("Saving..."):
        r = requests.put(f"{API_URL}/doctor/appointments/{appt_id}/video-link",
            json={"video_link": video_link})
        if r.status_code == 200:
            st.success("Video link saved")
        else:
            st.error(r.json().get("detail", "Failed — check if this is an Online appointment"))
```

---

## Patient Pages

### Browse Doctors Page
```python
# Patient browses and filters doctors by speciality, mode, availability
st.title("Browse Doctors")

col1, col2 = st.columns(2)
speciality = col1.text_input("Filter by Speciality")
mode = col2.selectbox("Consultation Mode", ["", "Online", "Offline"])

params = {}
if speciality: params["speciality"] = speciality
if mode: params["mode"] = mode

with st.spinner("Loading doctors..."):
    r = requests.get(f"{API_URL}/patient/doctors", params=params)
    if r.status_code == 200:
        st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
    else:
        st.error("Failed to load doctors")
```

### Book Appointment Page
```python
# Patient selects doctor, date, and available slot to book
st.title("Book Appointment")

doctor_id = st.text_input("Doctor ID")
date = st.date_input("Select Date")

if st.button("Find Available Slots"):
    with st.spinner("Loading slots..."):
        r = requests.get(f"{API_URL}/patient/slots",
            params={"doctor_id": doctor_id, "date": str(date)})
        if r.status_code == 200:
            slots = r.json()
            if slots:
                st.session_state["available_slots"] = slots
                st.dataframe(pd.DataFrame(slots), use_container_width=True)
            else:
                st.info("No available slots for this date")
        else:
            st.error("Failed to load slots")

slot_id = st.text_input("Enter Slot ID to Book")
if st.button("Confirm Booking"):
    with st.spinner("Booking..."):
        r = requests.post(f"{API_URL}/patient/appointments",
            json={"patient_id": st.session_state["user_id"], "slot_id": slot_id})
        if r.status_code == 200:
            data = r.json()
            st.success(f"Booked! Your token number is {data['token_number']}")
            st.write(f"Doctor: {data['doctor_name']}")
            st.write(f"Time: {data['slot_start']}")
            st.write(f"Mode: {data['mode']}")
        elif r.status_code == 409:
            st.error("This slot was just booked by someone else. Please choose another.")
        else:
            st.error("Booking failed")
```

### My Appointments Page (Patient)
```python
# Patient sees upcoming and past appointments with toggle
st.title("My Appointments")

tab1, tab2 = st.tabs(["Upcoming", "Past"])

with st.spinner("Loading..."):
    r = requests.get(f"{API_URL}/patient/appointments/{st.session_state['user_id']}")
    if r.status_code == 200:
        data = r.json()
        with tab1:
            if data["upcoming"]:
                st.dataframe(pd.DataFrame(data["upcoming"]), use_container_width=True)
                # Show video link or clinic info per appointment
                appt_id = st.text_input("Enter Appointment ID to view details")
                if st.button("Get Details"):
                    # Try video link first (online)
                    vr = requests.get(f"{API_URL}/patient/appointment/{appt_id}/video-link",
                        params={"patient_id": st.session_state["user_id"]})
                    if vr.status_code == 200:
                        st.write(f"Video Link: {vr.json()['video_link']}")
                    else:
                        # Try clinic info (offline)
                        cr = requests.get(f"{API_URL}/patient/appointment/{appt_id}/clinic-info")
                        if cr.status_code == 200:
                            info = cr.json()
                            st.write(f"Clinic Address: {info['clinic_address']}")
                            st.write(f"Date: {info['shift_date']} | {info['start_time']} - {info['end_time']}")
            else:
                st.info("No upcoming appointments")
        with tab2:
            if data["past"]:
                st.dataframe(pd.DataFrame(data["past"]), use_container_width=True)
            else:
                st.info("No past appointments")
    else:
        st.error("Failed to load appointments")
```

### My Prescriptions Page
```python
# Patient views all their prescriptions
st.title("My Prescriptions")
with st.spinner("Loading..."):
    r = requests.get(f"{API_URL}/patient/prescriptions/{st.session_state['user_id']}")
    if r.status_code == 200:
        data = r.json()
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("No prescriptions found")
    else:
        st.error("Failed to load prescriptions")
```

---

## API Configuration
```python
# Backend URL — change this if running on different port
API_URL = "http://localhost:8000"
```
