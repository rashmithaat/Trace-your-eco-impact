import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from fpdf import FPDF
import tempfile
import os
import plotly.io as pio

# API Base URL
API_URL = "http://127.0.0.1:8000"

# Fetch user data from API
def fetch_user_data(username, token):
    """Fetch user eco-points and progress data."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/user-data/{username}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch user data.")
        return None

# Clean text to remove unsupported Unicode characters
def clean_text(text):
    """Replace unsupported characters with plain alternatives."""
    replacements = {
        "₂": "2",  # Subscript 2 -> Normal 2
        "₃": "3",  # Subscript 3 -> Normal 3
        "°": " degrees",  # Degree symbol -> " degrees"
        "–": "-",  # En dash -> Hyphen
        "→": "->"  # Right arrow -> Arrow text
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text

# Generate PDF for dashboard summary
def generate_pdf(user_data, username):
    """Generate a PDF file with cleaned content and embed a graph image."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add cleaned text to the PDF
    pdf.cell(200, 10, txt=clean_text(f"Dashboard for {username}"), ln=True, align='C')
    pdf.cell(200, 10, txt=clean_text(f"Total Eco Points: {user_data['eco_points']}"), ln=True)
    pdf.cell(200, 10, txt=clean_text(f"Carbon Footprint: {user_data['carbon_footprint']} kg CO2e"), ln=True)

    # Generate Progress Over Time Graph as an image
    progress_df = pd.DataFrame(user_data["progress_over_time"])
    if not progress_df.empty:
        fig = px.line(progress_df, x=progress_df.index, y=["eco_points", "carbon_footprint"],
                      labels={"value": "Count", "index": "Measurement Instance", "variable": "Metric"},
                      title="Progress Over Time")
        temp_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        pio.write_image(fig, temp_img_path)  # Save the chart as a PNG image

        # Add the graph image to the PDF
        pdf.image(temp_img_path, x=10, y=50, w=190)  # Adjust position and size

        # Cleanup the temporary image file
        os.remove(temp_img_path)

    # Save PDF to a temporary file
    temp_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(temp_pdf_path)
    return temp_pdf_path

# Display Dashboard
def display_dashboard(username, token):
    """Display user dashboard with metrics, graphs, and share option."""
    st.title(f"🌿 Welcome, {username}!")

    # Fetch user data
    user_data = fetch_user_data(username, token)
    if not user_data:
        return

    # Display Metrics
    st.subheader("Your Eco-Friendly Progress")
    st.metric("Total Eco Points", user_data["eco_points"])
    st.metric("Carbon Footprint", f"{user_data['carbon_footprint']} kg CO2e")

    # Progress Over Time Graph
    st.subheader("📊 Progress Over Time")
    progress_df = pd.DataFrame(user_data["progress_over_time"])
    if not progress_df.empty:
        progress_df.index.name = "Measurement Instance"
        fig = px.line(progress_df, x=progress_df.index, y=["eco_points", "carbon_footprint"],
                      labels={"value": "Count", "variable": "Metric"})
        st.plotly_chart(fig)

    # Suggested Actions
    st.subheader("🌍 Suggested Eco-Friendly Actions")
    for action in user_data.get("suggested_actions", []):
        st.markdown(f"✅ {action}")

    # Share Dashboard PDF
    st.subheader("📤 Share Your Dashboard")
    email = st.text_input("Enter recipient's email:")
    if st.button("Share Dashboard PDF"):
        if email:
            pdf_path = generate_pdf(user_data, username)
            st.write(f"PDF Path: {pdf_path}")  # Debugging: Display generated PDF path
            
            response = requests.post(f"{API_URL}/share-dashboard/",
                                     json={"username": username, "email": email, "content": user_data})
            
            # Debugging: Log API response details
            st.write(f"API Response Status Code: {response.status_code}")
            st.write(f"API Response Text: {response.text}")
            
            if response.status_code == 200:
                st.success("Dashboard shared successfully!")
            else:
                st.error(f"Failed to share dashboard: {response.text}")
        else:
            st.error("Please enter a valid email address.")

# Run Dashboard
if __name__ == "__main__":
    # Example usage (for testing):
    # Replace "DemoUser" and "test_token" with your values.
    st.set_page_config(layout="wide")
    display_dashboard("DemoUser", "test_token")
