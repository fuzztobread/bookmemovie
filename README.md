# Bookmemovie:Movie Ticketing System

Complete movie booking system with FastAPI backend + Streamlit frontend, featuring JWT authentication and real-time seat management.

##  Key Features

- ** Customer**: Browse movies, book seats, manage bookings
- ** Admin**: Manage movies/events, view analytics, system control
- ** Security**: JWT auth, role-based access, session persistence

##  Quick Setup

### 1. Install & Configure
```bash
# Clone and setup
git clone <your-repo-url>
cd bookmemovie
python -m venv menv
source menv/bin/activate  # Windows: menv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn streamlit python-dotenv passlib[bcrypt] python-jose[cryptography] sqlalchemy pandas requests pydantic-settings

# Setup environment
cp .env.example app/.env
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
# Add the generated SECRET_KEY to app/.env
```

### 2. Run Applications
```bash
# Terminal 1: Backend API
cd app && uvicorn main:app --reload

# Terminal 2: Frontend Dashboard  
streamlit run app/dashboard.py
```

**Access**: Frontend → `http://localhost:8501` | API Docs → `http://localhost:8000/docs`

## 👥 Complete Admin Workflow

### Initial Setup
1. **Open dashboard** → Go to **"Admin Setup"** tab
2. **Create admin**: `admin@company.com` / `secure123`
3. **Login** with admin credentials

### Movie Management Flow
```bash
# 1. Add Movies
Admin Panel → Manage Movies → Add New Movie
Title: "Spider-Man: No Way Home"
Description: "Epic superhero adventure..."
→ Click "Add Movie"

# 2. Edit Movies  
→ Click "✏️ Edit" next to movie
→ Update title/description
→ Click "Save Changes"

# 3. Delete Movies
→ Click "🗑️ Delete" (only if no active events)
```

### Event Management Flow
```bash
# 1. Schedule Events
Admin Panel → Manage Events → Schedule New Event
Movie: "Spider-Man: No Way Home"
Date: "2025-07-15" 
Time: "19:30"
Seats: 30
→ Click "Schedule Event"

# 2. Edit Events
→ Click "✏️ Edit" next to event
→ Change movie/date/time
→ Click "Save Changes"

# 3. Delete Events  
→ Click "🗑️ Delete" (protected if bookings exist)
```

### Monitor System
```bash
Admin Panel → System Overview
- View total events, seats, bookings
- Check occupancy rates
- Monitor real-time statistics
- Export event data
```

## 🎫 Customer Usage Flow

### Booking Process
1. **Browse**: View movies → Select showtime
2. **Seats**: Choose seats on visual map
3. **Book**: Enter details → Get booking reference
4. **Pay**: Confirm payment within 10 minutes
5. **Manage**: Cancel booking if needed

## 🔌 Essential API Endpoints

### Authentication
```bash
POST /api/auth/create-admin    # Setup admin
POST /api/auth/login          # Get JWT token
GET  /api/auth/me             # User info
```

### Customer Operations
```bash
GET  /api/events                      # List movies/showtimes
GET  /api/events/{id}/seats          # Seat availability
POST /api/book-seats                 # Book tickets
POST /api/confirm-payment            # Confirm booking
POST /api/cancel-booking             # Cancel booking
```

### Admin Operations  
```bash
# Movies
GET    /api/admin/movies           # List all movies
POST   /api/admin/movies           # Add movie
PUT    /api/admin/movies/{id}      # Edit movie
DELETE /api/admin/movies/{id}      # Delete movie

# Events  
GET    /api/admin/events           # List events + stats
POST   /api/admin/events           # Create event
PUT    /api/admin/events/{id}      # Edit event
DELETE /api/admin/events/{id}      # Delete event
```

##  Authentication Flow

```bash
# 1. Login → Get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@company.com", "password": "secure123"}'

# Response: {"access_token": "eyJhbGc...", "user": {...}}

# 2. Use token for protected endpoints
curl -X GET "http://localhost:8000/api/admin/movies" \
  -H "Authorization: Bearer eyJhbGc..."
```

## 📁 Project Structure

```
bookmemovie/
├── app/
│   ├── main.py              # FastAPI app
│   ├── dashboard.py         # Streamlit UI
│   ├── config.py           # Environment config
│   ├── database.py         # DB connection
│   ├── core/auth.py        # JWT authentication
│   ├── models/             # SQLAlchemy models
│   ├── routes/             # API endpoints
│   └── schemas/            # Pydantic schemas
├── .env.example            # Config template
└── README.md
```

##  Configuration

### Required Environment Variables
```bash
# app/.env
SECRET_KEY=your-32-char-secret-key-here
DATABASE_URL=sqlite:///./movie_ticketing.db
DEBUG=true
BASE_URL=http://localhost:8000
```

### Production Settings
```bash
SECRET_KEY=strong-production-secret
DATABASE_URL=postgresql://user:pass@localhost/moviedb
DEBUG=false
BASE_URL=https://your-domain.com
```

##  Tech Stack

**Backend**: FastAPI, SQLAlchemy, JWT, Pydantic  
**Frontend**: Streamlit, Pandas, Requests  
**Database**: SQLite (dev) / PostgreSQL (prod)  
**Auth**: JWT tokens with bcrypt password hashing

##  Key Business Logic

- **Seat Locking**: 10-minute reservation window
- **Role Protection**: Admin-only movie/event management  
- **Booking Protection**: Cannot delete events with active bookings
- **Session Persistence**: Login survives page reloads
- **Real-time Updates**: Live seat availability

---


