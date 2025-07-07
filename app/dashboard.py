import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# API base URL
API_BASE = "http://localhost:8000/api"

# Page config
st.set_page_config(page_title="🎬 Movie Ticketing System", layout="wide")

# Initialize session state
if 'selected_event' not in st.session_state:
    st.session_state.selected_event = None
if 'seats_loaded' not in st.session_state:
    st.session_state.seats_loaded = False
if 'seat_data' not in st.session_state:
    st.session_state.seat_data = None

# Title
st.title("🎬 Movie Ticketing System")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page:", ["🎥 Browse Movies", "🎫 Book Tickets", "📊 Admin Panel"])

if page == "🎥 Browse Movies":
    st.header("Available Movies")
    
    try:
        # Fetch events from API
        response = requests.get(f"{API_BASE}/events")
        if response.status_code == 200:
            events = response.json()
            
            if events:
                # Display movies in a nice format
                for event in events:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 2])
                        
                        with col1:
                            st.subheader(event['movie_title'])
                            st.write(event['movie_description'])
                        
                        with col2:
                            st.write(f"**Show Time:** {event['start_time'][:19]}")
                            st.write(f"**Event ID:** {event['event_id']}")
                        
                        with col3:
                            if st.button(f"Book Now", key=f"book_{event['event_id']}"):
                                st.session_state.selected_event = event['event_id']
                                st.success(f"✅ Selected Event {event['event_id']}! Go to 'Book Tickets' page to continue.")
                        
                        st.divider()
            else:
                st.info("No movies available at the moment.")
        else:
            st.error("Failed to fetch movies from API")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")

elif page == "🎫 Book Tickets":
    st.header("Book Movie Tickets")
    
    # Show selected event from browse page
    if st.session_state.selected_event:
        st.info(f"📍 Selected Event: {st.session_state.selected_event}")
    
    # Event selection
    default_event = st.session_state.selected_event if st.session_state.selected_event else 1
    event_id = st.number_input("Enter Event ID:", min_value=1, value=default_event)
    
    # Load seats button
    if st.button("🎭 Load Seats", type="primary"):
        with st.spinner("Loading seats..."):
            try:
                # Fetch seats for the event
                response = requests.get(f"{API_BASE}/events/{event_id}/seats")
                if response.status_code == 200:
                    st.session_state.seat_data = response.json()
                    st.session_state.seats_loaded = True
                    st.session_state.current_event_id = event_id
                    st.success("✅ Seats loaded successfully!")
                else:
                    st.error("Failed to load seats")
                    st.session_state.seats_loaded = False
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.seats_loaded = False
    
    # Display seats if loaded
    if st.session_state.seats_loaded and st.session_state.seat_data:
        data = st.session_state.seat_data
        seats = data['seats']
        
        st.divider()
        st.subheader(f"🎭 Seat Map for Event {st.session_state.current_event_id}")
        
        # Display seat statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Seats", len(seats))
        with col2:
            available = len([s for s in seats if s['status'] == 'open'])
            st.metric("🟢 Available", available)
        with col3:
            locked = len([s for s in seats if s['status'] == 'locked'])
            st.metric("🟡 Locked", locked)
        with col4:
            booked = len([s for s in seats if s['status'] == 'booked'])
            st.metric("🔴 Booked", booked)
        
        # Create a visual seat map
        st.subheader("Seat Layout")
        
        # Group seats by row for better display
        seat_rows = {}
        for seat in seats:
            row = seat['description'].split()[1]  # Extract row from "Row A Seat 1"
            if row not in seat_rows:
                seat_rows[row] = []
            seat_rows[row].append(seat)
        
        # Display seats row by row
        for row_name in sorted(seat_rows.keys()):
            row_seats = sorted(seat_rows[row_name], key=lambda x: int(x['description'].split()[-1]))
            
            st.write(f"**Row {row_name}**")
            cols = st.columns(len(row_seats))
            
            for i, seat in enumerate(row_seats):
                with cols[i]:
                    status_color = {"open": "🟢", "locked": "🟡", "booked": "🔴"}
                    color = status_color.get(seat['status'], "⚪")
                    st.write(f"{color} {seat['seat_id']}")
                    st.caption(f"${seat['price']}")
        
        st.divider()
        
        # Booking form
        st.subheader("📝 Book Your Seats")
        
        # Multi-select for seat IDs - use a form to prevent auto-refresh
        with st.form("booking_form"):
            available_seats = [s['seat_id'] for s in seats if s['status'] == 'open']
            
            if available_seats:
                selected_seats = st.multiselect(
                    "Select Seats (you can select multiple):", 
                    available_seats,
                    help="Choose the seats you want to book"
                )
                
                user_email = st.text_input(
                    "Your Email:", 
                    placeholder="user@example.com",
                    help="We'll send your booking confirmation here"
                )
                
                # Show selected seats info
                if selected_seats:
                    total_price = sum([s['price'] for s in seats if s['seat_id'] in selected_seats])
                    st.info(f"💰 Selected {len(selected_seats)} seats - Total: ${total_price}")
                
                submitted = st.form_submit_button("🎫 Book Selected Seats", type="primary")
                
                if submitted and selected_seats and user_email:
                    with st.spinner("Processing your booking..."):
                        try:
                            booking_data = {
                                "seat_ids": selected_seats,
                                "user_email": user_email
                            }
                            
                            response = requests.post(f"{API_BASE}/book-seats", json=booking_data)
                            
                            if response.status_code == 200:
                                result = response.json()
                                st.success("✅ Booking Successful!")
                                
                                # Display booking details in a nice format
                                with st.container():
                                    st.write("### 🎟️ Booking Details")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Booking Reference:** `{result['booking_reference']}`")
                                        st.write(f"**Total Amount:** ${result['total_amount']}")
                                    with col2:
                                        st.write(f"**Seats:** {', '.join(map(str, result['seat_ids']))}")
                                        st.write(f"**Status:** {result['status']}")
                                    
                                    st.info(f"⏰ {result['message']}")
                                
                                # Store booking reference in session
                                st.session_state.last_booking = result['booking_reference']
                                
                                # Force refresh seat data
                                st.session_state.seats_loaded = False
                                
                            else:
                                error_detail = response.json().get('detail', 'Unknown error')
                                st.error(f"❌ Booking failed: {error_detail}")
                        except Exception as e:
                            st.error(f"❌ Booking error: {e}")
                elif submitted and not selected_seats:
                    st.warning("⚠️ Please select at least one seat")
                elif submitted and not user_email:
                    st.warning("⚠️ Please enter your email address")
            else:
                st.warning("😔 No seats available for this event")
    
    # Payment/Cancellation section
    if 'last_booking' in st.session_state:
        st.divider()
        st.subheader("💳 Payment & Booking Management")
        
        with st.form("payment_form"):
            booking_ref = st.text_input(
                "Booking Reference:", 
                value=st.session_state.last_booking,
                help="Your booking reference code"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                confirm_payment = st.form_submit_button("✅ Confirm Payment", type="primary")
            with col2:
                cancel_booking = st.form_submit_button("❌ Cancel Booking", type="secondary")
            
            if confirm_payment and booking_ref:
                try:
                    response = requests.post(f"{API_BASE}/confirm-payment", 
                                           json={"booking_reference": booking_ref})
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['message']}")
                        st.balloons()  # Celebration effect!
                    else:
                        error_detail = response.json().get('detail', 'Unknown error')
                        st.error(f"❌ Payment failed: {error_detail}")
                except Exception as e:
                    st.error(f"❌ Payment error: {e}")
            
            if cancel_booking and booking_ref:
                try:
                    response = requests.post(f"{API_BASE}/cancel-booking", 
                                           json={"booking_reference": booking_ref})
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['message']}")
                        if 'last_booking' in st.session_state:
                            del st.session_state.last_booking
                        # Force refresh seat data
                        st.session_state.seats_loaded = False
                    else:
                        error_detail = response.json().get('detail', 'Unknown error')
                        st.error(f"❌ Cancellation failed: {error_detail}")
                except Exception as e:
                    st.error(f"❌ Cancellation error: {e}")

elif page == "📊 Admin Panel":
    st.header("📊 Admin Dashboard")
    
    # Auto-refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh", type="primary"):
            st.rerun()
    
    # System stats
    st.subheader("System Overview")
    
    try:
        # Get all events
        response = requests.get(f"{API_BASE}/events")
        if response.status_code == 200:
            events = response.json()
            
            total_events = len(events)
            
            # Get seat statistics for all events
            total_seats = 0
            total_booked = 0
            total_locked = 0
            
            with st.spinner("Loading system statistics..."):
                for event in events:
                    try:
                        seat_response = requests.get(f"{API_BASE}/events/{event['event_id']}/seats")
                        if seat_response.status_code == 200:
                            seat_data = seat_response.json()
                            seats = seat_data['seats']
                            
                            total_seats += len(seats)
                            total_booked += len([s for s in seats if s['status'] == 'booked'])
                            total_locked += len([s for s in seats if s['status'] == 'locked'])
                    except:
                        continue
            
            # Display metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("🎬 Events", total_events)
            with col2:
                st.metric("🎭 Total Seats", total_seats)
            with col3:
                st.metric("🔴 Booked", total_booked)
            with col4:
                st.metric("🟡 Locked", total_locked)
            with col5:
                available = total_seats - total_booked - total_locked
                st.metric("🟢 Available", available)
            
            # Revenue calculation
            if total_seats > 0:
                occupancy_rate = ((total_booked + total_locked) / total_seats) * 100
                st.metric("📈 Occupancy Rate", f"{occupancy_rate:.1f}%")
            
            # Show events table
            if events:
                st.divider()
                st.subheader("📋 All Events")
                events_df = pd.DataFrame(events)
                st.dataframe(events_df, use_container_width=True)
                
                # Detailed seat info for each event
                st.subheader("🎭 Seat Details by Event")
                for event in events:
                    with st.expander(f"Event {event['event_id']}: {event['movie_title']}"):
                        try:
                            seat_response = requests.get(f"{API_BASE}/events/{event['event_id']}/seats")
                            if seat_response.status_code == 200:
                                seat_data = seat_response.json()
                                seats = seat_data['seats']
                                
                                # Create seat status summary
                                seat_df = pd.DataFrame(seats)
                                status_summary = seat_df['status'].value_counts()
                                
                                # Display status summary
                                cols = st.columns(len(status_summary))
                                for i, (status, count) in enumerate(status_summary.items()):
                                    with cols[i]:
                                        color_map = {"open": "🟢", "locked": "🟡", "booked": "🔴"}
                                        st.metric(f"{color_map.get(status, '⚪')} {status.title()}", count)
                                
                                # Show seat details table
                                st.dataframe(seat_df, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error loading seats for event {event['event_id']}: {e}")
        else:
            st.error("Failed to fetch events from API")
        
    except Exception as e:
        st.error(f"Error loading admin data: {e}")

# Footer
st.divider()
st.caption("🎬 Movie Ticketing System - Built with FastAPI + Streamlit")
if st.button("ℹ️ About"):
    st.info("""
    **Features:**
    - 🎥 Browse available movies and showtimes
    - 🎫 Interactive seat selection and booking
    - 💳 Payment confirmation system
    - 📊 Real-time admin dashboard
    - 🔄 Auto-refresh capabilities
    
    **Tech Stack:** FastAPI (Backend) + Streamlit (Frontend) + SQLite (Database)
    """)
