import streamlit as st
import requests
from dashboard import display_dashboard

# API Base URL
API_URL = "http://127.0.0.1:8000"

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "token" not in st.session_state:
    st.session_state.token = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# Function to login user
def login_user(username, password):
    response = requests.post(f"{API_URL}/login/", json={"username": username, "password": password})
    if response.status_code == 200:
        data = response.json()
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.token = data["token"]
        return True
    else:
        st.error("Login Failed: Invalid Credentials")
        return False

# Function to sign up user
def signup_user(username, password):
    response = requests.post(f"{API_URL}/signup/", json={"username": username, "password": password})
    if response.status_code == 200:
        st.success("Account created successfully! Please log in.")
        return True
    else:
        st.error("Signup Failed. Username may already exist.")
        return False

# Function to calculate eco-points
def submit_eco_points(data, files, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/calculate-eco-points/", data=data, files=files, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to calculate eco points.")
        return None

# Login or Sign Up Page
if not st.session_state.authenticated:
    st.title("🌱 Eco Adventure - Login / Sign Up")
    menu = st.sidebar.radio("Choose Option", ["Login", "Sign Up"])

    if menu == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username and password:
                if login_user(username, password):
                    st.success("Login Successful!")
            else:
                st.error("Please enter both username and password.")

    elif menu == "Sign Up":
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            if new_username and new_password:
                signup_user(new_username, new_password)
            else:
                st.error("Please fill all fields.")
else:
    # Main Application (Authenticated User)
    st.title("🌿 Eco Adventure Dashboard")

    # Sidebar Navigation
    menu = st.sidebar.radio("Navigation", ["Submit Eco Actions", "Go to Dashboard"])

    if menu == "Go to Dashboard":
        # Import and display the dashboard
        try:
            display_dashboard(st.session_state.username, st.session_state.token)
        except Exception as e:
            st.error(f"Error loading dashboard: {e}")
    else:
        # Input Form for Eco Points Calculation
        st.subheader("🌍 Enter Your Daily Activity Details")

        # Input fields
        car_km = st.number_input("🚗 Kilometers traveled by car:", min_value=0, step=1)
        public_transport_km = st.number_input("🚌 Kilometers traveled by public transport:", min_value=0, step=1)
        bike_km = st.number_input("🚲 Kilometers traveled by bike:", min_value=0, step=1)
        electricity_kwh = st.number_input("⚡ Daily electricity usage (kWh):", min_value=0, step=1)
        air_conditioning_hours = st.number_input("🌬️ Hours of air conditioning used:", min_value=0, step=1)
        heating_hours = st.number_input("🔥 Hours of heating used:", min_value=0, step=1)
        meat_consumption = st.selectbox("🍖 Do you consume meat?", ["Yes", "No"])
        dairy_consumption = st.selectbox("🥛 Do you consume dairy?", ["Yes", "No"])
        recycle = st.selectbox("♻️ Do you recycle?", ["Yes", "No"])
        compost = st.selectbox("🌱 Do you compost?", ["Yes", "No"])
        eco_actions = st.multiselect("🌿 Select additional eco actions you performed:", options=["Planted a tree", "Used public transport", "Recycled items"])

        # File uploader for proof
        eco_action_img = st.file_uploader("📷 Upload proof of eco-friendly action", type=["png", "jpg", "jpeg"])

        # Submit Button
        if st.button("Submit"):
            if st.session_state.username and st.session_state.token:
                # Prepare data for submission
                data = {
                    "username": st.session_state.username,
                    "car_km": car_km,
                    "public_transport_km": public_transport_km,
                    "bike_km": bike_km,
                    "electricity_kwh": electricity_kwh,
                    "air_conditioning_hours": air_conditioning_hours,
                    "heating_hours": heating_hours,
                    "meat_consumption": meat_consumption,
                    "dairy_consumption": dairy_consumption,
                    "recycle": recycle,
                    "compost": compost,
                }
                files = {"image": eco_action_img} if eco_action_img else None

                # Submit data to API
                result = submit_eco_points(data, files, st.session_state.token)
                if result:
                    st.success("✅ Eco Points and Carbon Footprint Calculated Successfully!")
                    st.markdown(f"### 🌿 Eco Points: **{result['eco_points']}**")
                    st.markdown(f"### 🏭 Carbon Footprint: **{result['carbon_footprint']} kg CO₂e**")
                else:
                    st.error("Something went wrong. Please try again.")
            else:
                st.error("User not authenticated. Please log in again.")
