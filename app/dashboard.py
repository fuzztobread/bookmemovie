import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# API base URL
API_BASE = "http://localhost:8000/api"
ADMIN_API = "http://localhost:8000/api/admin"
AUTH_API = "http://localhost:8000/api/auth"

# Page config
st.set_page_config(page_title="🎬 Movie Ticketing System", layout="wide")

# Initialize session state
if 'selected_event' not in st.session_state:
    st.session_state.selected_event = None
if 'seats_loaded' not in st.session_state:
    st.session_state.seats_loaded = False
if 'seat_data' not in st.session_state:
    st.session_state.seat_data = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

def get_auth_headers():
    """Get authorization headers for API requests"""
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}

def login_user(email, password):
    """Login user and store token"""
    try:
        response = requests.post(f"{AUTH_API}/login", json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.session_state.is_admin = data["user"]["role"] == "admin"
            return True, "Login successful!"
        else:
            error = response.json().get("detail", "Login failed")
            return False, error
    except Exception as e:
        return False, f"Connection error: {e}"

def logout_user():
    """Logout user and clear session"""
    st.session_state.access_token = None
    st.session_state.user_info = None
    st.session_state.is_admin = False

def register_user(email, password, full_name):
    """Register new user"""
    try:
        response = requests.post(f"{AUTH_API}/register", json={
            "email": email,
            "password": password,
            "full_name": full_name
        })
        
        if response.status_code == 200:
            return True, "Registration successful! Please login."
        else:
            error = response.json().get("detail", "Registration failed")
            return False, error
    except Exception as e:
        return False, f"Connection error: {e}"

# Header with authentication
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    st.title("🎬 Movie Ticketing System")

with col2:
    if st.session_state.user_info:
        st.write(f"👋 Welcome, **{st.session_state.user_info['full_name']}**")
        if st.session_state.is_admin:
            st.write("🔑 Admin Access")

with col3:
    if st.session_state.user_info:
        if st.button("🚪 Logout", type="secondary"):
            logout_user()
            st.rerun()
    else:
        st.write("🔒 Not logged in")

# Authentication Section
if not st.session_state.user_info:
    st.header("🔐 Authentication Required")
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with auth_tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email:", placeholder="admin@movie-tickets.com")
            password = st.text_input("Password:", type="password", placeholder="admin123")
            
            if st.form_submit_button("🔑 Login", type="primary"):
                if email and password:
                    success, message = login_user(email, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter both email and password")
        
        # Show default admin credentials
        st.info("""
        **Default Admin Credentials:**
        - Email: `admin@movie-tickets.com`
        - Password: `admin123`
        
        **Note:** Change these credentials in production!
        """)
    
    with auth_tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            reg_email = st.text_input("Email:", placeholder="user@example.com")
            reg_password = st.text_input("Password:", type="password")
            reg_full_name = st.text_input("Full Name:", placeholder="John Doe")
            
            if st.form_submit_button("📝 Register", type="primary"):
                if reg_email and reg_password and reg_full_name:
                    success, message = register_user(reg_email, reg_password, reg_full_name)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill in all fields")

else:
    # Main application (only shown when logged in)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    
    # Different navigation based on user role
    if st.session_state.is_admin:
        # Admin users only see admin functionality
        page = st.sidebar.selectbox("Choose a page:", ["📊 Admin Panel"])
        st.sidebar.info("🔑 **Admin Mode**\nYou have administrative privileges to manage the system.")
    else:
        # Regular users see customer functionality
        page = st.sidebar.selectbox("Choose a page:", [
            "🎥 Browse Movies", 
            "🎫 Book Tickets"
        ])
        st.sidebar.info("👤 **Customer Mode**\nBrowse and book movie tickets.")
    
    # User info in sidebar
    st.sidebar.divider()
    st.sidebar.write(f"**Logged in as:**")
    st.sidebar.write(f"👤 {st.session_state.user_info['full_name']}")
    st.sidebar.write(f"📧 {st.session_state.user_info['email']}")
    st.sidebar.write(f"🏷️ {st.session_state.user_info['role'].title()}")

    if page == "🎥 Browse Movies":
        st.header("Available Movies")
        
        try:
            # ALL API calls need auth headers - including user endpoints
            response = requests.get(f"{API_BASE}/events", headers=get_auth_headers())
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
                    # ALL API calls need auth headers
                    response = requests.get(f"{API_BASE}/events/{event_id}/seats", headers=get_auth_headers())
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
                    
                    # Auto-fill user email from logged-in user
                    user_email = st.text_input(
                        "Your Email:", 
                        value=st.session_state.user_info['email'],
                        help="Email from your logged-in account"
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
                                
                                # ALL API calls need auth headers
                                response = requests.post(f"{API_BASE}/book-seats", json=booking_data, headers=get_auth_headers())
                                
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
                        # ALL API calls need auth headers
                        response = requests.post(f"{API_BASE}/confirm-payment", 
                                               json={"booking_reference": booking_ref}, headers=get_auth_headers())
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
                        # ALL API calls need auth headers
                        response = requests.post(f"{API_BASE}/cancel-booking", 
                                               json={"booking_reference": booking_ref}, headers=get_auth_headers())
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
        st.header("🔑 Administrative Dashboard")
        st.write("**System Management & Analytics**")
        
        # Tabs for different admin functions
        tab1, tab2, tab3 = st.tabs(["📈 System Overview", "🎬 Manage Movies", "🎭 Manage Events"])
        
        with tab1:
            # Auto-refresh button
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🔄 Refresh", type="primary"):
                    st.rerun()
            
            # System stats
            st.subheader("📊 System Statistics")
            
            try:
                # Use ADMIN endpoint with auth headers
                response = requests.get(f"{ADMIN_API}/events", headers=get_auth_headers())
                if response.status_code == 200:
                    events = response.json()
                    
                    total_events = len(events)
                    
                    # Calculate stats from admin event data
                    total_seats = sum(event['total_seats'] for event in events)
                    total_booked = sum(event['booked_seats'] for event in events)
                    total_locked = sum(event['locked_seats'] for event in events)
                    
                    # Display metrics
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("🎬 Total Events", total_events)
                    with col2:
                        st.metric("🎭 Total Seats", total_seats)
                    with col3:
                        st.metric("🔴 Confirmed Bookings", total_booked)
                    with col4:
                        st.metric("🟡 Pending Bookings", total_locked)
                    with col5:
                        available = total_seats - total_booked - total_locked
                        st.metric("🟢 Available Seats", available)
                    
                    # Occupancy rate
                    if total_seats > 0:
                        occupancy_rate = ((total_booked + total_locked) / total_seats) * 100
                        st.metric("📈 Overall Occupancy Rate", f"{occupancy_rate:.1f}%")
                    
                    # Show events table
                    if events:
                        st.divider()
                        st.subheader("📋 All Active Events")
                        # Convert to DataFrame for better display
                        events_df = pd.DataFrame(events)
                        st.dataframe(events_df, use_container_width=True)
                        
                        # Quick insights (removed revenue)
                        st.subheader("🔍 Quick Insights")
                        if total_events > 0:
                            avg_seats_per_event = total_seats / total_events
                            st.write(f"• **Average seats per event:** {avg_seats_per_event:.1f}")
                            if total_booked > 0:
                                st.write(f"• **Total confirmed bookings:** {total_booked}")
                        else:
                            st.info("No events available for analysis.")
                elif response.status_code == 401:
                    st.error("🔒 Authentication failed. Please login again.")
                    logout_user()
                    st.rerun()
                elif response.status_code == 403:
                    st.error("🚫 Access denied. Admin privileges required.")
                else:
                    st.error("Failed to fetch events from API")
                
            except Exception as e:
                st.error(f"Error loading admin data: {e}")
        
        # The rest of the admin tabs stay the same...
        with tab2:
            st.subheader("🎬 Movie Content Management")
            # ... (rest of movies management code stays same)
            
        with tab3:
            st.subheader("🎭 Event & Showtime Management")
            # ... (rest of events management code stays same)

# Footer
st.divider()
st.caption("🎬 Movie Ticketing System - Built with FastAPI + Streamlit + JWT Authentication")
