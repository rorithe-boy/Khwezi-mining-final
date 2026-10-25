"""
BETTER MINING - KHWEZI MINING - GROUP 25
Beginner-friendly Streamlit project (fictional classroom data only).

Each page is a short if/elif block. The helper functions below
only read/save CSV files and calculate availability/risk/alerts.
Run with: streamlit run app.py
"""
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Better Mining | Group 25", page_icon="⛏️", layout="wide")

# Mining background image
import base64
background_file = Path(__file__).parent / "mine_background.png"
if background_file.exists():
    background_bytes = base64.b64encode(background_file.read_bytes()).decode("utf-8")
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(5, 20, 30, 0.70), rgba(5, 20, 30, 0.78)),
                    url('data:image/png;base64,{background_bytes}') center / cover fixed;
    }}
    [data-testid="stMainBlockContainer"] {{
        background: rgba(6, 23, 34, 0.72);
        padding: 2rem; border-radius: 16px;
    }}
    [data-testid="stSidebar"] {{background: rgba(7, 25, 37, 0.96);}}
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] label {{color: white;}}
    </style>
    """, unsafe_allow_html=True)


# STEP 1: User accounts and permissions (classroom demonstration only)
users = {
    "admin": ("Admin123!", "Administrator"),
    "safety": ("Safety123!", "Safety Officer"),
    "engineer": ("Engineer123!", "Mining Engineer"),
    "maintenance": ("Maint123!", "Maintenance Engineer"),
    "manager": ("Manager123!", "Manager")
}

all_pages = ["Dashboard", "Workers", "Incidents", "Equipment", "Maintenance",
             "Risk Assessment", "Alerts", "Analysis", "Reports", "Manage Users"]

permissions = {
    "Administrator": all_pages,
    "Safety Officer": ["Dashboard", "Workers", "Incidents", "Risk Assessment", "Alerts", "Analysis", "Reports"],
    "Mining Engineer": ["Dashboard", "Workers", "Incidents", "Equipment", "Maintenance", "Risk Assessment", "Alerts", "Analysis", "Reports"],
    "Maintenance Engineer": ["Dashboard", "Equipment", "Maintenance", "Alerts", "Analysis", "Reports"],
    "Manager": ["Dashboard", "Workers", "Incidents", "Equipment", "Maintenance", "Risk Assessment", "Alerts", "Analysis", "Reports"]
}

# STEP 2: CSV files (easy to open in Excel)
data_folder = Path(__file__).parent / "data"
data_folder.mkdir(exist_ok=True)

columns = {
    "workers.csv": ["Worker ID", "Name", "Department", "Job Role", "Shift", "PPE", "Training", "Fatigue", "Safety Observation", "Previous Incidents", "Risk Level"],
    "incidents.csv": ["Incident ID", "Date", "Time", "Location", "Department", "Shift", "Type", "Severity", "Injury", "Lost Time", "Cause", "Corrective Action", "Status"],
    "equipment.csv": ["Equipment ID", "Type", "Manufacturer", "Temperature", "Vibration", "Operating Hours", "Downtime", "Fuel Consumption", "Brake Status", "Tyre Status", "Engine Status", "Maintenance Due", "Maintenance Status"],
    "observations.csv": ["Location", "Hazard", "Likelihood", "Consequence", "Score", "Level"]
}

def read_data(filename):
    path = data_folder / filename
    if not path.exists():
        pd.DataFrame(columns=columns[filename]).to_csv(path, index=False)
    return pd.read_csv(path).reindex(columns=columns[filename]).fillna("")

def save_data(filename, new_values):
    table = read_data(filename)
    table.loc[len(table)] = new_values
    table.to_csv(data_folder / filename, index=False)

def calculate_availability(hours, downtime):
    total = hours + downtime
    if total == 0:
        return 0
    return hours / total * 100

def check_condition(temperature, vibration):
    # Project-brief demonstration thresholds, not real mine safety limits.
    if temperature > 100 or vibration > 8:
        return "CRITICAL"
    elif temperature >= 80 or vibration >= 5:
        return "WARNING"
    else:
        return "NORMAL"

def classify_risk(score):
    if score <= 4:
        return "LOW"
    elif score <= 9:
        return "MEDIUM"
    elif score <= 16:
        return "HIGH"
    else:
        return "CRITICAL"

# STEP 3: Login
if "username" not in st.session_state:
    st.session_state.username = ""

if st.session_state.username == "":
    st.title("⛏️ Better Mining")
    st.subheader("Khwezi Mining - Group 25")
    st.write("Mining Safety and Equipment Monitoring")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Log in")
    if login:
        name = username.lower().strip()
        if name in users and password == users[name][0]:
            st.session_state.username = name
            st.rerun()
        else:
            st.error("Wrong username or password")
    st.caption("Demonstration accounts only. Do not enter real personal or mine data.")
    st.stop()

role = users[st.session_state.username][1]
st.sidebar.title("⛏️ Better Mining")
st.sidebar.write("Logged in:", st.session_state.username)
st.sidebar.write("Role:", role)
menu_choice = st.sidebar.radio("Choose a page", permissions[role])
if st.sidebar.button("Log out"):
    st.session_state.username = ""
    st.rerun()

# STEP 4: Load stored information
workers = read_data("workers.csv")
incidents = read_data("incidents.csv")
equipment = read_data("equipment.csv")
observations = read_data("observations.csv")

# STEP 5: Generate alerts from stored information
alerts = []

for _, machine in equipment.iterrows():
    machine_id = str(machine["Equipment ID"])
    temperature = float(machine["Temperature"])
    vibration = float(machine["Vibration"])
    hours = float(machine["Operating Hours"])
    downtime = float(machine["Downtime"])
    condition = check_condition(temperature, vibration)

    if condition != "NORMAL":
        alerts.append(condition + ": Check equipment " + machine_id)
    if machine["Maintenance Due"] == "Yes":
        alerts.append("MAINTENANCE DUE: " + machine_id)
    if machine["Maintenance Status"] == "Overdue":
        alerts.append("OVERDUE MAINTENANCE: " + machine_id)
    if machine["Brake Status"] == "Needs inspection" or machine["Tyre Status"] == "Needs inspection" or machine["Engine Status"] == "Needs inspection":
        alerts.append("EQUIPMENT INSPECTION: " + machine_id)
    if downtime > 50:
        alerts.append("EXCESSIVE DOWNTIME: " + machine_id)
    if machine["Maintenance Status"] == "Under maintenance":
        alerts.append("UNDER MAINTENANCE: " + machine_id)
    if calculate_availability(hours, downtime) < 70:
        alerts.append("LOW AVAILABILITY: " + machine_id)

for _, worker in workers.iterrows():
    if worker["PPE"] == "No" or worker["Training"] == "No" or worker["Fatigue"] == "High" or worker["Risk Level"] in ["High", "Critical"]:
        alerts.append("WORKER SAFETY: " + str(worker["Worker ID"]))

for _, incident in incidents.iterrows():
    if incident["Severity"] == "Critical":
        alerts.append("CRITICAL INCIDENT: " + str(incident["Incident ID"]))

for _, observation in observations.iterrows():
    if observation["Level"] in ["HIGH", "CRITICAL"]:
        alerts.append("HIGH RISK: " + str(observation["Location"]))

# STEP 6: Application pages

# MEMBER 4 - Code 1: Dashboard
if menu_choice == "Dashboard":
    st.header("Mining Dashboard")
    a, b, c, d = st.columns(4)
    a.metric("Workers", len(workers))
    b.metric("Incidents", len(incidents))
    c.metric("Equipment", len(equipment))
    d.metric("Alerts", len(alerts))

    if len(incidents) > 0:
        st.subheader("Incidents by severity")
        st.bar_chart(incidents["Severity"].value_counts())

    if len(workers) > 0:
        compliant = (workers["PPE"] == "Yes").sum()
        ppe_percent = compliant / len(workers) * 100
        st.metric("PPE compliance", f"{ppe_percent:.1f}%")

    st.write("Near misses:", int((incidents["Type"] == "Near miss").sum()))
    st.write("High/Critical risks:", int(observations["Level"].isin(["HIGH", "CRITICAL"]).sum()))
    st.write("Available equipment:", int((equipment["Maintenance Status"] == "Operational").sum()))
    st.write("Under maintenance:", int((equipment["Maintenance Status"] == "Under maintenance").sum()))
    st.write("Critical equipment conditions:", sum(check_condition(float(m["Temperature"]), float(m["Vibration"])) == "CRITICAL" for _, m in equipment.iterrows()))
    if len(equipment) > 0:
        availability_list = []
        for _, m in equipment.iterrows():
            availability_list.append(calculate_availability(float(m["Operating Hours"]), float(m["Downtime"])))
        st.metric("Average availability", f"{sum(availability_list)/len(availability_list):.1f}%")
    st.write("Critical incident alerts:", int((incidents["Severity"] == "Critical").sum()))

# MEMBER 1 - Code 1: Worker safety
elif menu_choice == "Workers":
    st.header("Worker Health and Safety")
    with st.form("worker_form"):
        worker_id = st.text_input("Worker ID")
        name = st.text_input("Worker Name")
        department = st.selectbox("Department", ["Mining", "Safety", "Maintenance", "Processing"])
        job_role = st.text_input("Job role")
        shift = st.selectbox("Shift", ["Day", "Night"])
        observation = st.text_input("Safety observation")
        previous_incidents = st.number_input("Previous incidents", min_value=0)
        risk = st.selectbox("Worker risk level", ["Low", "Medium", "High", "Critical"])
        ppe = st.selectbox("Wearing PPE?", ["Yes", "No"])
        training = st.selectbox("Safety training complete?", ["Yes", "No"])
        fatigue = st.selectbox("Fatigue", ["Low", "Medium", "High"])
        save = st.form_submit_button("Save Worker")

    if ppe == "No":
        st.error("WARNING: PPE not worn!")
    if training == "No":
        st.warning("WARNING: Safety training incomplete!")
    if fatigue == "High":
        st.error("WARNING: Worker fatigue is high!")

    if save:
        if worker_id.strip() == "" or name.strip() == "":
            st.error("Enter Worker ID and Name")
        elif worker_id in workers["Worker ID"].astype(str).values:
            st.error("This Worker ID already exists")
        else:
            save_data("workers.csv", [worker_id, name, department, job_role, shift, ppe, training, fatigue, observation, previous_incidents, risk])
            st.success("Worker saved!")
            st.rerun()
    st.dataframe(workers, use_container_width=True)

# MEMBER 1 - Code 2: Incident reporting
elif menu_choice == "Incidents":
    st.header("Incident Reporting")
    with st.form("incident_form"):
        incident_id = st.text_input("Incident ID")
        date = st.date_input("Date")
        incident_time = st.time_input("Time")
        location = st.text_input("Location")
        injury = st.selectbox("Injury occurred?", ["No", "Yes"])
        lost_time = st.selectbox("Lost-time injury?", ["No", "Yes"])
        cause = st.text_input("Cause")
        corrective_action = st.text_input("Corrective action")
        department = st.selectbox("Department", ["Mining", "Safety", "Maintenance", "Processing"])
        shift = st.selectbox("Shift", ["Day", "Night"])
        incident_type = st.selectbox("Incident Type", ["Near miss", "Injury", "Equipment", "Unsafe act"])
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "Investigating", "Closed"])
        save = st.form_submit_button("Save Incident")

    if severity == "Critical":
        st.error("CRITICAL INCIDENT!")
    elif severity == "High":
        st.warning("HIGH SEVERITY INCIDENT!")

    if save:
        if incident_id.strip() == "":
            st.error("Enter an Incident ID")
        elif incident_id in incidents["Incident ID"].astype(str).values:
            st.error("This Incident ID already exists")
        else:
            save_data("incidents.csv", [incident_id, str(date), str(incident_time), location, department, shift,
                                        incident_type, severity, injury, lost_time, cause, corrective_action, status])
            st.success("Incident saved!")
            st.rerun()

    search = st.text_input("Search Incident ID")
    if search:
        incidents = incidents[incidents["Incident ID"].astype(str).str.contains(search, case=False, regex=False)]
    severity_filter = st.selectbox("Filter severity", ["All", "Low", "Medium", "High", "Critical"])
    if severity_filter != "All":
        incidents = incidents[incidents["Severity"] == severity_filter]
    department_filter = st.selectbox("Filter department", ["All", "Mining", "Safety", "Maintenance", "Processing"])
    if department_filter != "All":
        incidents = incidents[incidents["Department"] == department_filter]
    st.write("Matching incidents:", len(incidents))
    if len(incidents) > 0:
        st.subheader("Incident trends by date")
        st.bar_chart(incidents["Date"].value_counts().sort_index())
    st.dataframe(incidents, use_container_width=True)

# MEMBER 2 - Code 1: Equipment monitoring
elif menu_choice == "Equipment":
    st.header("Equipment Monitoring")
    with st.form("equipment_form"):
        equipment_id = st.text_input("Equipment ID")
        machine_type = st.selectbox("Equipment Type", ["Haul truck", "Excavator", "Loader", "Drill", "Crusher", "Conveyor"])
        manufacturer = st.text_input("Manufacturer")
        fuel = st.number_input("Fuel consumption (L/h)", min_value=0.0)
        brakes = st.selectbox("Brake status", ["Good", "Needs inspection"])
        tyres = st.selectbox("Tyre status", ["Good", "Needs inspection"])
        engine = st.selectbox("Engine status", ["Good", "Needs inspection"])
        temperature = st.number_input("Temperature (°C)", min_value=0.0, value=75.0)
        vibration = st.number_input("Vibration (mm/s)", min_value=0.0, value=3.0)
        hours = st.number_input("Operating Hours", min_value=0.0, value=100.0)
        downtime = st.number_input("Downtime Hours", min_value=0.0, value=10.0)
        due = st.selectbox("Maintenance Due?", ["No", "Yes"])
        status = st.selectbox("Maintenance Status", ["Operational", "Under maintenance", "Overdue"])
        save = st.form_submit_button("Save Equipment")

    condition = check_condition(temperature, vibration)
    if condition == "CRITICAL":
        st.error("CRITICAL: Temperature or vibration too high!")
    elif condition == "WARNING":
        st.warning("WARNING: Monitor equipment!")
    else:
        st.success("NORMAL equipment condition")

    if save:
        if equipment_id.strip() == "":
            st.error("Enter Equipment ID")
        elif equipment_id in equipment["Equipment ID"].astype(str).values:
            st.error("This Equipment ID already exists")
        else:
            save_data("equipment.csv", [equipment_id, machine_type, manufacturer, temperature, vibration,
                                         hours, downtime, fuel, brakes, tyres, engine, due, status])
            st.success("Equipment saved!")
            st.rerun()
    st.dataframe(equipment, use_container_width=True)

# MEMBER 2 - Code 2: Maintenance
elif menu_choice == "Maintenance":
    st.header("Equipment Maintenance")
    if equipment.empty:
        st.info("Add equipment first")
    else:
        percentages = []
        for _, machine in equipment.iterrows():
            hours = float(machine["Operating Hours"])
            downtime = float(machine["Downtime"])
            percent = calculate_availability(hours, downtime)
            percentages.append(round(percent, 2))

        report = equipment.copy()
        report["Availability (%)"] = percentages
        st.dataframe(report, use_container_width=True)
        st.metric("Average availability", f"{report['Availability (%)'].mean():.1f}%")

        for _, machine in report.iterrows():
            if machine["Maintenance Due"] == "Yes" or machine["Maintenance Status"] == "Overdue":
                st.warning("MAINTENANCE REQUIRED: " + str(machine["Equipment ID"]))
            if machine["Availability (%)"] < 70:
                st.error("LOW AVAILABILITY: " + str(machine["Equipment ID"]))
            if float(machine["Downtime"]) > 50:
                st.warning("EXCESSIVE DOWNTIME: " + str(machine["Equipment ID"]))

# MEMBER 3 - Code 1: Risk assessment
elif menu_choice == "Risk Assessment":
    st.header("Risk Assessment")
    with st.form("risk_form"):
        location = st.text_input("Location")
        hazard = st.text_input("Hazard")
        likelihood = st.slider("Likelihood (1-5)", 1, 5, 3)
        consequence = st.slider("Consequence (1-5)", 1, 5, 3)
        save = st.form_submit_button("Save Risk")

    risk_score = likelihood * consequence
    level = classify_risk(risk_score)

    if level == "LOW":
        st.success(f"Risk Score: {risk_score} → LOW")
    elif level == "MEDIUM":
        st.warning(f"Risk Score: {risk_score} → MEDIUM")
    elif level == "HIGH":
        st.error(f"Risk Score: {risk_score} → HIGH")
    else:
        st.error(f"Risk Score: {risk_score} → CRITICAL")

    if save:
        if location.strip() == "" or hazard.strip() == "":
            st.error("Enter a location and hazard")
        else:
            save_data("observations.csv", [location, hazard, likelihood,
                                           consequence, risk_score, level])
            st.success("Risk saved!")
            st.rerun()
    st.dataframe(observations, use_container_width=True)

# MEMBER 3 - Code 2: Automatic alerts
elif menu_choice == "Alerts":
    st.header("Automatic Safety Alerts")
    if len(alerts) == 0:
        st.success("No current alerts")
    else:
        st.metric("Active alerts", len(alerts))
        for message in alerts:
            st.warning(message)
    st.caption("Prototype thresholds only. Not certified mine safety limits.")

# MEMBER 4 - Code 2: Analysis and reports
elif menu_choice == "Analysis":
    st.header("Mining Data Analysis")
    if len(incidents) > 0:
        shift = st.selectbox("Filter by Shift", ["All", "Day", "Night"])
        if shift != "All":
            incidents = incidents[incidents["Shift"] == shift]
        st.metric("Incidents", len(incidents))
        st.write("Near misses:", int((incidents["Type"] == "Near miss").sum()))
        st.bar_chart(incidents["Department"].value_counts())
    else:
        st.info("No incidents to analyse yet")

    if len(equipment) > 0:
        availability_values = []
        for _, machine in equipment.iterrows():
            percent = calculate_availability(float(machine["Operating Hours"]),
                                             float(machine["Downtime"]))
            availability_values.append(percent)
        chart_data = equipment.copy()
        chart_data["Availability (%)"] = availability_values
        st.subheader("Equipment Availability")
        st.bar_chart(chart_data.set_index("Equipment ID")["Availability (%)"])
        st.subheader("Downtime by equipment")
        st.bar_chart(chart_data.set_index("Equipment ID")["Downtime"])
    if len(observations) > 0:
        st.subheader("Risk levels")
        st.bar_chart(observations["Level"].value_counts())

elif menu_choice == "Reports":
    st.header("Download CSV Reports")
    for filename in columns:
        table = read_data(filename)
        st.download_button("Download " + filename,
                           table.to_csv(index=False),
                           file_name=filename,
                           mime="text/csv")

elif menu_choice == "Manage Users":
    st.header("Demo User Accounts")
    st.write("Administrator-only page. Demo accounts cannot be changed here.")
    names = []
    for username in users:
        names.append({"Username": username, "Role": users[username][1]})
    st.dataframe(pd.DataFrame(names), use_container_width=True)

st.caption("Better Mining | Khwezi Mining | Group 25 | Classroom prototype")
