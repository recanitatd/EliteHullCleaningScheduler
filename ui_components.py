# ui_components.py
import streamlit as st
import pandas as pd
from data_manager import save_history

def display_diver_selection(num_pairs, divers_df):
    """Display diver selection interface."""
    pairs = []
    for i in range(num_pairs):
        col1, col2 = st.columns(2)
        with col1:
            diver1 = st.selectbox(f"Diver 1 for Pair {i+1}", ["None"] + divers_df["name"].tolist(), key=f"diver1_{i}", index=0)
        with col2:
            diver2 = st.selectbox(f"Diver 2 for Pair {i+1}", ["None"] + divers_df["name"].tolist(), key=f"diver2_{i}", index=0)
        pairs.append((diver1, diver2 if diver2 != "None" and diver2 != diver1 else None))
    return pairs

def display_schedules(schedules):
    """Display generated schedules."""
    for pair in schedules:
        diver1, diver2 = pair
        if diver1 != "None":
            schedule = schedules[pair]
            st.write(f"### Schedule for {diver1} {'& ' + diver2 if diver2 else '(Solo)'}")
            if schedule and isinstance(schedule, list):  # Ensure schedule is a list of dicts
                st.table(pd.DataFrame(schedule)[["Boat ID/Name", "Size (ft)", "Location/Address", "Due Date", "total_pay"]])
                total_pay = sum(b["total_pay"] * (0.6 if not diver2 else 0.3) for b in schedule if isinstance(b, dict))
                st.write(f"Estimated pay per diver: ${total_pay:.2f} | Area: {schedule[0].get('city', 'Multiple Cities') if schedule else 'N/A'}")
            else:
                st.write("No boats assigned to this schedule.")

def display_manage_schedules(schedules, available_boats):
    """Display manage schedules interface."""
    if schedules:
        st.subheader("Manage Schedules")
        for i, (pair, schedule) in enumerate(schedules.items()):
            if pair[0] != "None" or pair[1] != "None":
                diver1, diver2 = pair
                st.write(f"### Schedule for {diver1} {'& ' + diver2 if diver2 else '(Solo)'}")
                if schedule and isinstance(schedule, list):  # Ensure schedule is a list
                    schedule_df = pd.DataFrame([b if isinstance(b, dict) else b.to_dict() for b in schedule])[["Boat ID/Name", "Size (ft)", "Location/Address", "Due Date", "total_pay"]]
                    st.table(schedule_df)
                else:
                    st.write("No boats assigned to this schedule.")

                # Add a boat
                add_boat = st.selectbox(f"Add boat to {diver1}'s schedule", ["None"] + available_boats["Boat ID/Name"].tolist(), key=f"add_{i}")
                if add_boat != "None":
                    boat_to_add = available_boats[available_boats["Boat ID/Name"] == add_boat].iloc[0].to_dict()  # Ensure dictionary
                    if st.button(f"Add {add_boat} to {diver1}'s schedule", key=f"add_btn_{i}"):
                        schedules[pair].append(boat_to_add)
                        available_boats.drop(available_boats[available_boats["Boat ID/Name"] == add_boat].index, inplace=True)
                        st.rerun()

                # Delete a boat
                if schedule and isinstance(schedule, list):
                    delete_boat = st.selectbox(f"Delete boat from {diver1}'s schedule", ["None"] + [b["Boat ID/Name"] for b in schedule], key=f"delete_{i}")
                    if delete_boat != "None":
                        if st.button(f"Delete {delete_boat} from {diver1}'s schedule", key=f"delete_btn_{i}"):
                            boat_to_delete = next(b for b in schedule if b["Boat ID/Name"] == delete_boat)
                            schedules[pair] = [b for b in schedule if b["Boat ID/Name"] != delete_boat]
                            available_boats = pd.concat([available_boats, pd.DataFrame([boat_to_delete])], ignore_index=True)
                            st.rerun()

def display_completion_tab(schedules, status_log, completed_boats, missed_boats, history_file):
    """Display completion tab interface."""
    if st.session_state.get("show_completion", False):
        st.title("Complete Schedules")
        for i, (pair, schedule) in enumerate(schedules.items()):
            if pair[0] != "None" or pair[1] != "None":
                diver1, diver2 = pair
                st.write(f"### Schedule for {diver1} {'& ' + diver2 if diver2 else '(Solo)'}")
                if schedule and isinstance(schedule, list):  # Ensure schedule is a list
                    for j, boat in enumerate(schedule):
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col1:
                            if st.button("Completed", key=f"complete_{i}_{diver1}_{j}_{boat['Boat ID/Name']}"):
                                completed_boats = pd.concat([completed_boats, pd.DataFrame([boat])], ignore_index=True)
                                if pair not in status_log:
                                    status_log[pair] = []
                                status_log[pair].append((boat["Boat ID/Name"], "Completed"))
                                schedules[pair] = [b for b in schedule if b["Boat ID/Name"] != boat["Boat ID/Name"]]
                                save_history(completed_boats, missed_boats, history_file)
                                st.rerun()
                        with col3:
                            if st.button("Missed", key=f"missed_{i}_{diver1}_{j}_{boat['Boat ID/Name']}"):
                                missed_boats = pd.concat([missed_boats, pd.DataFrame([boat])], ignore_index=True)
                                if pair not in status_log:
                                    status_log[pair] = []
                                status_log[pair].append((boat["Boat ID/Name"], "Missed"))
                                schedules[pair] = [b for b in schedule if b["Boat ID/Name"] != boat["Boat ID/Name"]]
                                save_history(completed_boats, missed_boats, history_file)
                                st.rerun()
                        with col2:
                            st.write(boat["Boat ID/Name"])
                else:
                    st.write("No boats remaining in this schedule.")

                # Display status log for this pair
                if pair in status_log and status_log[pair]:
                    st.subheader("Completed/Missed Log")
                    log_df = pd.DataFrame(status_log[pair], columns=["Boat ID/Name", "Status"])
                    st.table(log_df)