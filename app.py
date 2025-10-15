# app.py
import streamlit as st
import pandas as pd
from data_manager import load_data, load_history, save_history
from schedule_logic import generate_schedules
from ui_components import display_diver_selection, display_schedules, display_manage_schedules, display_completion_tab
import datetime

# Load the boat data
boats_df = load_data("mock_boats.csv")

# Define diver profiles
divers = [
    {"name": "Terry St. Onge", "address": "5131 Rushbrooke Rd, Land O Lakes, FL 34638", "experience": "A"},
    {"name": "Maria Gonzalez", "address": "7423 Gulf Blvd, New Port Richey, FL 34652", "experience": "A"},
    {"name": "James Carter", "address": "3209 Tarpon Springs Dr, Tarpon Springs, FL 34689", "experience": "A"},
    {"name": "Lisa Nguyen", "address": "5901 Clearwater Ave, Clearwater, FL 33767", "experience": "A"},
    {"name": "Robert Kim", "address": "4512 4th St N, St. Petersburg, FL 33701", "experience": "B"},
    {"name": "Emily Patel", "address": "1234 Davis Islands Blvd, Tampa, FL 33602", "experience": "B"},
    {"name": "David Lee", "address": "8901 Harbour Island Dr, Tampa, FL 33602", "experience": "B"},
    {"name": "Sarah Johnson", "address": "6789 Apollo Beach Blvd, Apollo Beach, FL 33572", "experience": "B"},
    {"name": "Michael Brown", "address": "2345 Gulfview Dr, Clearwater, FL 33767", "experience": "C"},
    {"name": "Jessica White", "address": "5678 Pine St, St. Petersburg, FL 33701", "experience": "C"}
]
divers_df = pd.DataFrame(divers)

# Calculate pay per boat
boats_df["total_pay"] = boats_df["Size (ft)"].apply(lambda x: x * 2.50 if x <= 49 else x * 3.00)

# Load history
history_file = "hull_cleaning_history.csv"
completed_boats, missed_boats = load_history(history_file)

# Initialize session state
if "completed_boats" not in st.session_state:
    st.session_state.completed_boats = completed_boats
if "missed_boats" not in st.session_state:
    st.session_state.missed_boats = missed_boats
if "schedules" not in st.session_state:
    st.session_state.schedules = {}
if "available_boats" not in st.session_state:
    st.session_state.available_boats = pd.DataFrame(columns=boats_df.columns)
if "status_log" not in st.session_state:
    st.session_state.status_log = {}
if "num_pairs" not in st.session_state:
    st.session_state.num_pairs = 2  # Default value

# Streamlit app (Main Tab)
st.title("Elite Hull Cleaning Scheduler")
st.write(f"Welcome to the scheduling tool! (Today: {datetime.datetime.now().strftime('%B %d, %Y %I:%M %p EDT')})")

# Filter boats due today or overdue, including previously missed boats
current_date = datetime.datetime.now()  # 03:33 PM EDT, October 15, 2025
boats_df["Due Date"] = pd.to_datetime(boats_df["Due Date"])
initial_due_boats = boats_df[boats_df["Due Date"] <= current_date]
due_boats = pd.concat([initial_due_boats, st.session_state.missed_boats]).drop_duplicates(subset=["Boat ID/Name"])
st.session_state.available_boats = due_boats.copy()

st.subheader("Boats Due Today or Overdue")
st.write(due_boats[["Boat ID/Name", "Size (ft)", "Location/Address", "Due Date", "total_pay"]])

# Display diver selection with number of pairs input
st.subheader("Assign Divers")
num_pairs = st.number_input("Number of diver pairs/lists (e.g., 2-4)", min_value=1, max_value=5, value=st.session_state.get("num_pairs", 2), key="num_pairs_input")
st.session_state.num_pairs = num_pairs  # Update session state
pairs = display_diver_selection(num_pairs, divers_df)

# Generate schedules
if st.button("Generate Schedules"):
    st.session_state.schedules, missed_boats = generate_schedules(st.session_state.available_boats, pairs)
    st.session_state.missed_boats = missed_boats
    st.session_state.available_boats = st.session_state.available_boats.drop(missed_boats.index, errors='ignore')
    display_schedules(st.session_state.schedules)
    st.subheader("Missed Boats (for next day)")
    st.write(missed_boats if not missed_boats.empty else "No missed boats.")

# Manage schedules
display_manage_schedules(st.session_state.schedules, st.session_state.available_boats)

# Complete button to open new tab
if st.button("Complete Schedules"):
    st.session_state.show_completion = True
    st.rerun()

# Completion Tab
display_completion_tab(st.session_state.schedules, st.session_state.status_log, st.session_state.completed_boats, st.session_state.missed_boats, history_file)