# 🎬 Movie Ticketing System

Complete movie booking system with FastAPI backend + Streamlit frontend, featuring JWT authentication and real-time seat management.

## ✨ Key Features

- **🎫 Customer**: Browse movies, book seats, manage bookings
- **👨‍💼 Admin**: Manage movies/events, view analytics, system control
- **🔐 Security**: JWT auth, role-based access, session persistence

##  Libraries Used

```bash
# Core Framework
fastapi>=0.104.1              # High-performance web framework
uvicorn[standard]>=0.24.0      # ASGI server for FastAPI
streamlit>=1.28.0              # Interactive web applications

# Database & ORM
sqlalchemy>=2.0.23             # SQL toolkit and ORM
pandas>=2.1.3                  # Data manipulation and analysis

# Authentication & Security  
python-jose[cryptography]>=3.3.0   # JWT token handling
passlib[bcrypt]>=1.7.4         # Password hashing with bcrypt
python-multipart>=0.0.6       # Form data parsing

# Configuration & HTTP
python-dotenv>=1.0.0           # Environment variables
pydantic-settings>=2.0.3      # Settings management
requests>=2.31.0               # HTTP client library

# Data Validation
pydantic>=2.5.0                # Data validation using Python type hints
```

## 🚀 Quick Setup

### 1. Install & Configure
```bash
# Clone and setup
git clone https://github.com/fuzztobread/bookmemovie.git
cd bookmemovie
python -m venv menv
source menv/bin/activate  # Windows: menv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

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

##  Complete Admin Workflow

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
- Monitor real-time statistics
- Export event data
```

##  Customer Usage Flow

### Booking Process
1. **Browse**: View movies → Select showtime
2. **Seats**: Choose seats on visual map
3. **Book**: Enter details → Get booking reference
4. **Pay**: Confirm payment within 10 minutes
5. **Manage**: Cancel booking if needed

##  Essential API Endpoints

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

## 🎯 Key Business Logic

- **Seat Locking**: 10-minute reservation window
- **Role Protection**: Admin-only movie/event management  
- **Booking Protection**: Cannot delete events with active bookings
- **Session Persistence**: Login survives page reloads

---


