import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# API base URL
API_BASE = "http://localhost:8000/api"
ADMIN_API = "http://localhost:8000/api/admin"

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
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "🎬 Manage Movies", "🎭 Manage Events"])
    
    with tab1:
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
            else:
                st.error("Failed to fetch events from API")
            
        except Exception as e:
            st.error(f"Error loading admin data: {e}")
    
    with tab2:
        st.subheader("🎬 Movie Management")
        
        # Display existing movies
        try:
            response = requests.get(f"{ADMIN_API}/movies")
            if response.status_code == 200:
                movies = response.json()
                
                if movies:
                    st.write("### Current Movies")
                    movies_df = pd.DataFrame(movies)
                    
                    # Display movies with action buttons
                    for movie in movies:
                        with st.container():
                            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                            
                            with col1:
                                st.write(f"**{movie['title']}**")
                                st.caption(movie['description'] or "No description")
                            
                            with col2:
                                st.write(f"ID: {movie['id']}")
                            
                            with col3:
                                # Edit button
                                if st.button("✏️ Edit", key=f"edit_movie_{movie['id']}"):
                                    st.session_state[f"editing_movie_{movie['id']}"] = True
                            
                            with col4:
                                # Delete button
                                if st.button("🗑️ Delete", key=f"delete_movie_{movie['id']}", type="secondary"):
                                    if st.confirm(f"Delete '{movie['title']}'?"):
                                        try:
                                            del_response = requests.delete(f"{ADMIN_API}/movies/{movie['id']}")
                                            if del_response.status_code == 200:
                                                st.success("Movie deleted successfully!")
                                                st.rerun()
                                            else:
                                                st.error("Failed to delete movie")
                                        except Exception as e:
                                            st.error(f"Error: {e}")
                            
                            # Edit form (shown when edit button is clicked)
                            if st.session_state.get(f"editing_movie_{movie['id']}", False):
                                with st.form(f"edit_movie_form_{movie['id']}"):
                                    st.write(f"### Edit: {movie['title']}")
                                    new_title = st.text_input("Title:", value=movie['title'])
                                    new_description = st.text_area("Description:", value=movie['description'] or "")
                                    
                                    col_save, col_cancel = st.columns(2)
                                    with col_save:
                                        if st.form_submit_button("💾 Save Changes", type="primary"):
                                            try:
                                                update_data = {
                                                    "title": new_title,
                                                    "description": new_description
                                                }
                                                update_response = requests.put(f"{ADMIN_API}/movies/{movie['id']}", json=update_data)
                                                if update_response.status_code == 200:
                                                    st.success("Movie updated successfully!")
                                                    st.session_state[f"editing_movie_{movie['id']}"] = False
                                                    st.rerun()
                                                else:
                                                    st.error("Failed to update movie")
                                            except Exception as e:
                                                st.error(f"Error: {e}")
                                    
                                    with col_cancel:
                                        if st.form_submit_button("❌ Cancel"):
                                            st.session_state[f"editing_movie_{movie['id']}"] = False
                                            st.rerun()
                            
                            st.divider()
                else:
                    st.info("No movies found")
        except Exception as e:
            st.error(f"Error loading movies: {e}")
        
        # Add new movie form
        st.divider()
        st.subheader("➕ Add New Movie")
        
        with st.form("add_movie_form"):
            movie_title = st.text_input("Movie Title:", placeholder="Enter movie title")
            movie_description = st.text_area("Description:", placeholder="Enter movie description (optional)")
            
            if st.form_submit_button("🎬 Add Movie", type="primary"):
                if movie_title:
                    try:
                        movie_data = {
                            "title": movie_title,
                            "description": movie_description if movie_description else None
                        }
                        
                        response = requests.post(f"{ADMIN_API}/movies", json=movie_data)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Movie '{result['title']}' added successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to add movie")
                    except Exception as e:
                        st.error(f"Error adding movie: {e}")
                else:
                    st.warning("Please enter a movie title")
    
    with tab3:
        st.subheader("🎭 Event Management")
        
        # Display existing events
        try:
            response = requests.get(f"{ADMIN_API}/events")
            if response.status_code == 200:
                events = response.json()
                
                if events:
                    st.write("### Current Events")
                    
                    # Display events with action buttons
                    for event in events:
                        with st.container():
                            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                            
                            with col1:
                                st.write(f"**{event['movie_title']}**")
                                st.caption(f"Start: {event['start_time'][:19]}")
                            
                            with col2:
                                st.write(f"ID: {event['id']}")
                                st.write(f"🎭 {event['available_seats']}/{event['total_seats']} available")
                            
                            with col3:
                                # Edit button
                                if st.button("✏️ Edit", key=f"edit_event_{event['id']}"):
                                    st.session_state[f"editing_event_{event['id']}"] = True
                            
                            with col4:
                                # Delete button
                                if st.button("🗑️ Delete", key=f"delete_event_{event['id']}", type="secondary"):
                                    if event['booked_seats'] > 0:
                                        st.error(f"Cannot delete: {event['booked_seats']} seats are booked")
                                    else:
                                        try:
                                            del_response = requests.delete(f"{ADMIN_API}/events/{event['id']}")
                                            if del_response.status_code == 200:
                                                st.success("Event deleted successfully!")
                                                st.rerun()
                                            else:
                                                st.error("Failed to delete event")
                                        except Exception as e:
                                            st.error(f"Error: {e}")
                            
                            # Edit form (shown when edit button is clicked)
                            if st.session_state.get(f"editing_event_{event['id']}", False):
                                with st.form(f"edit_event_form_{event['id']}"):
                                    st.write(f"### Edit Event: {event['movie_title']}")
                                    
                                    # Get movies for dropdown
                                    movies_response = requests.get(f"{ADMIN_API}/movies")
                                    if movies_response.status_code == 200:
                                        movies = movies_response.json()
                                        movie_options = {movie['title']: movie['id'] for movie in movies}
                                        
                                        current_movie = next((m['title'] for m in movies if m['id'] == event['movie_id']), None)
                                        new_movie = st.selectbox("Movie:", options=list(movie_options.keys()), 
                                                                index=list(movie_options.keys()).index(current_movie) if current_movie else 0)
                                        
                                        # Parse current datetime
                                        current_time = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                                        
                                        new_date = st.date_input("Date:", value=current_time.date())
                                        new_time = st.time_input("Time:", value=current_time.time())
                                        
                                        col_save, col_cancel = st.columns(2)
                                        with col_save:
                                            if st.form_submit_button("💾 Save Changes", type="primary"):
                                                try:
                                                    # Combine date and time
                                                    new_datetime = datetime.combine(new_date, new_time)
                                                    
                                                    update_data = {
                                                        "movie_id": movie_options[new_movie],
                                                        "start_time": new_datetime.isoformat()
                                                    }
                                                    update_response = requests.put(f"{ADMIN_API}/events/{event['id']}", json=update_data)
                                                    if update_response.status_code == 200:
                                                        st.success("Event updated successfully!")
                                                        st.session_state[f"editing_event_{event['id']}"] = False
                                                        st.rerun()
                                                    else:
                                                        st.error("Failed to update event")
                                                except Exception as e:
                                                    st.error(f"Error: {e}")
                                        
                                        with col_cancel:
                                            if st.form_submit_button("❌ Cancel"):
                                                st.session_state[f"editing_event_{event['id']}"] = False
                                                st.rerun()
                            
                            st.divider()
                else:
                    st.info("No events found")
        except Exception as e:
            st.error(f"Error loading events: {e}")
        
        # Add new event form
        st.divider()
        st.subheader("➕ Add New Event")
        
        with st.form("add_event_form"):
            # Get movies for dropdown
            try:
                movies_response = requests.get(f"{ADMIN_API}/movies")
                if movies_response.status_code == 200:
                    movies = movies_response.json()
                    
                    if movies:
                        movie_options = {movie['title']: movie['id'] for movie in movies}
                        selected_movie = st.selectbox("Select Movie:", options=list(movie_options.keys()))
                        
                        event_date = st.date_input("Event Date:")
                        event_time = st.time_input("Event Time:")
                        total_seats = st.number_input("Total Seats:", min_value=1, value=25, max_value=100)
                        
                        if st.form_submit_button("🎭 Add Event", type="primary"):
                            try:
                                # Combine date and time
                                event_datetime = datetime.combine(event_date, event_time)
                                
                                event_data = {
                                    "movie_id": movie_options[selected_movie],
                                    "start_time": event_datetime.isoformat(),
                                    "total_seats": total_seats
                                }
                                
                                response = requests.post(f"{ADMIN_API}/events", json=event_data)
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    st.success(f"✅ Event for '{selected_movie}' added successfully with {result['total_seats']} seats!")
                                    st.rerun()
                                else:
                                    error_detail = response.json().get('detail', 'Unknown error')
                                    st.error(f"Failed to add event: {error_detail}")
                            except Exception as e:
                                st.error(f"Error adding event: {e}")
                    else:
                        st.warning("⚠️ No movies available. Please add a movie first.")
                else:
                    st.error("Failed to load movies")
            except Exception as e:
                st.error(f"Error loading movies: {e}")

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
    - 🎬 Movie management (CRUD operations)
    - 🎭 Event management with auto seat generation
    - 🔄 Auto-refresh capabilities
    
    **Tech Stack:** FastAPI (Backend) + Streamlit (Frontend) + SQLite (Database)
    """)
