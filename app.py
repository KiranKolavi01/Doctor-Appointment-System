import streamlit as st
import requests
import pandas as pd

# API Configuration
API_URL = "http://localhost:8000"

st.set_page_config(layout="wide", page_title="Doctor Appointment System")

# CSS from FRONTEND_DESIGN_SYSTEM.md
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Michroma&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&display=swap');

/* Main body background and technical grid */
.stApp { 
    background-color: #F8F9FB; 
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
    color: #111827;
    background-image: 
        linear-gradient(#E5E7EB 1px, transparent 1px),
        linear-gradient(90deg, #E5E7EB 1px, transparent 1px);
    background-size: 40px 40px;
    background-position: center;
}

.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: radial-gradient(circle at 100% 0%, rgba(255, 255, 255, 0.9) 0%, rgba(248, 249, 251, 0.8) 100%);
    z-index: -1;
}

/* Headers */
h1, h2, h3 { 
    font-family: 'Montserrat', sans-serif !important;
    color: #111827 !important; 
    font-weight: 600 !important; 
    letter-spacing: 0.02em !important; 
    line-height: 1.2 !important;
    text-transform: none !important;
}

/* Branding Font */
.brand-font {
    font-family: 'Michroma', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: -0.02em !important;
    color: #000000 !important;
    font-size: 20px !important;
    margin-bottom: 0 !important;
}

/* Technical Status Labels */
.tech-label {
    font-size: 14px !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
    color: #6B7280 !important;
    margin-bottom: 4px !important;
}

/* Sidebar */
[data-testid="stSidebar"] { 
    background-color: #FFFFFF !important; 
    border-right: 1px solid #E5E7EB !important; 
    padding-top: 1rem;
}
[data-testid="stSidebarNav"] { display: none !important; }

/* Metrics */
[data-testid="stMetricValue"] { 
    color: #000000 !important; 
    font-weight: 800; 
    font-size: 2.2rem !important;
    letter-spacing: -0.03em;
}
[data-testid="stMetricLabel"] { 
    color: #6B7280 !important; 
    font-weight: 800; 
    font-size: 0.65rem; 
    text-transform: uppercase; 
    letter-spacing: 0.12em; 
}
[data-testid="stMetric"] { 
    background-color: #FFFFFF; 
    padding: 24px !important; 
    border-radius: 6px; 
    border: 1px solid #E5E7EB;
    box-shadow: none;
    transition: border-color 0.2s;
}
[data-testid="stMetric"]:hover { border-color: #34ACED; }

/* Navigation Radio */
div[data-testid="stRadio"] { padding: 0 !important; }
div[data-testid="stRadio"] [role="radiogroup"] { gap: 0.2rem !important; }
div[data-testid="stRadio"] label {
    padding: 8px 12px !important;
    margin-bottom: 2px !important;
    cursor: pointer !important;
    border-radius: 4px !important;
    border: 1px solid transparent !important;
    background-color: transparent !important;
}
div[data-testid="stRadio"] label:hover {
    background-color: #F8F9FB !important;
}
div[role="radiogroup"] > label > div:first-child,
div[data-testid="stRadio"] label div[data-baseweb="radio"],
.stRadio [role="radio"] > div:first-child,
.stRadio div[role="radiogroup"] label > div:first-child {
    display: none !important;
    opacity: 0 !important;
    width: 0px !important;
    height: 0px !important;
    overflow: hidden !important;
}
div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
    color: #4B5563 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: -0.01em !important;
}
div[data-testid="stRadio"] label[data-checked="true"] {
    background-color: #F0F9FF !important;
    border: 1px solid #BAE6FD !important;
}
div[data-testid="stRadio"] label[data-checked="true"] div[data-testid="stMarkdownContainer"] p {
    color: #34ACED !important;
    font-weight: 800 !important;
}

/* Dividers */
hr { border-bottom: 1px solid #E5E7EB !important; opacity: 1; margin: 2rem 0 !important; }

/* DataFrames */
[data-testid="stDataFrame"] { 
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB; 
    border-radius: 4px; 
    padding: 0;
}

/* Buttons */
.stButton > button, .stDownloadButton > button, div[data-testid="stDownloadButton"] > button {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 4px !important; 
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 0.75rem 1.5rem !important;
    text-transform: none !important;
    letter-spacing: -0.01em !important;
    transition: all 0.2s ease !important;
}
.stButton > button *, .stDownloadButton > button *, div[data-testid="stDownloadButton"] > button * {
    color: #FFFFFF !important;
}
.stButton > button:hover, .stDownloadButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {
    background-color: #34ACED !important;
    transform: translateY(-1px);
}
.stButton > button:active, .stDownloadButton > button:active, div[data-testid="stDownloadButton"] > button:active {
    transform: translateY(0);
}

/* Status Badges */
.status-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 100px;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    background-color: #F3F4F6;
    border: 1px solid #E5E7EB;
    color: #4B5563;
}
.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-right: 6px;
}
.dot-success { background-color: #10B981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.4); }
.dot-error { background-color: #EF4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }
.dot-warning { background-color: #F59E0B; box-shadow: 0 0 8px rgba(245, 158, 11, 0.4); }

/* Visualization Cards */
.viz-card {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 24px;
    margin-bottom: 24px;
}
</style>
""", unsafe_allow_html=True)

# Application specific overrides if unauthenticated
if "username" not in st.session_state or not st.session_state["username"]:
    st.markdown("""
        <style>
        .main > div { padding-top: 0rem !important; }
        .main .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            max-width: 100% !important;
        }
        [data-testid="stAppViewContainer"] > section.main { padding-top: 0 !important; }
        div[data-testid="stMarkdownContainer"] {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        div[data-testid="element-container"]:has(div[data-testid="stMarkdownContainer"]) {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)

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

def render_signup():
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
        st.rerun()

def render_signin():
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
                navigate_to("Dashboard")
                st.rerun()
            else:
                st.error("Invalid username or password")

    if st.button("Create Account"):
        navigate_to("signup")
        st.rerun()

def show_auth_pages():
    if st.session_state.get("current_page") == "signup":
        render_signup()
    else:
        render_signin()

def show_dashboard_for_role(role):
    # Sidebar Navigation
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
                    st.rerun()

        if st.button("Sign Out"):
            # Clear session and go back to sign in
            for key in ["username", "role", "user_id", "current_page"]:
                st.session_state[key] = ""
            st.query_params.clear()
            st.rerun()

    # Routing
    page = st.session_state.get("current_page")
    
    if role == "admin":
        if page == "Dashboard" or not page or page == "Home" or page == "signin":
            # Dashboard Page
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
        
        elif page == "Manage Doctors":
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

            with st.spinner("Loading doctors..."):
                r = requests.get(f"{API_URL}/admin/doctors")
                if r.status_code == 200:
                    df = pd.DataFrame(r.json())
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error("Failed to load doctors")
        
        elif page == "Manage Shifts":
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

        elif page == "Manage Slots":
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

        elif page == "All Appointments":
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

        elif page == "Patient Records":
            st.title("Patient Records")
            with st.spinner("Loading..."):
                r = requests.get(f"{API_URL}/admin/patients")
                if r.status_code == 200:
                    st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
                else:
                    st.error("Failed to load patients")

        elif page == "Audit Log":
            st.title("Audit Log")
            with st.spinner("Loading..."):
                r = requests.get(f"{API_URL}/admin/audit-log")
                if r.status_code == 200:
                    st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
                else:
                    st.error("Failed to load audit log")
                    
    elif role == "doctor":
        if page == "My Schedule" or not page or page == "Home" or page == "signin":
            st.title("My Weekly Schedule")
            with st.spinner("Loading schedule..."):
                r = requests.get(f"{API_URL}/doctor/schedule/{st.session_state['user_id']}")
                if r.status_code == 200:
                    st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
                else:
                    st.error("Failed to load schedule")
                    
        elif page == "My Appointments":
            st.title("My Appointments")
            with st.spinner("Loading..."):
                r = requests.get(f"{API_URL}/doctor/appointments/{st.session_state['user_id']}")
                if r.status_code == 200:
                    st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
                else:
                    st.error("Failed to load appointments")
        
        elif page == "Update Status":
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
                        
        elif page == "Add Prescription":
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
                        
        elif page == "Add Video Link":
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

    elif role == "patient":
        if page == "Browse Doctors" or not page or page == "Home" or page == "signin":
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

        elif page == "Book Appointment":
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

        elif page == "My Appointments":
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
        
        elif page == "My Prescriptions":
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

# If not logged in — show only Sign In or Sign Up
if not st.session_state["username"]:
    show_auth_pages()
else:
    show_dashboard_for_role(st.session_state["role"])
