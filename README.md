# 🎬 Movie Ticketing System

A complete movie ticket booking system with FastAPI backend and Streamlit frontend, featuring JWT authentication, role-based access control, and real-time seat management.

##  Features

###  **Customer Features**
- **Browse Movies**: View available movies with showtimes
- **Interactive Seat Selection**: Visual seat map with real-time availability
- **Seat Booking**: Select multiple seats with automatic pricing
- **Payment System**: Secure booking confirmation and payment processing
- **Booking Management**: Cancel bookings with automatic seat release
- **Session Persistence**: Login state preserved across page reloads

###  **Admin Features**
- **Admin Dashboard**: Comprehensive system overview and analytics
- **Movie Management**: Add, edit, and delete movies with descriptions
- **Event Management**: Schedule showtimes with automatic seat generation
- **Real-time Analytics**: Track bookings, occupancy rates, and seat statistics
- **Business Logic Protection**: Prevent deletion of events with active bookings

###  **Security Features**
- **JWT Authentication**: Secure token-based authentication
- **Role-based Access**: Separate user and admin permissions
- **Password Hashing**: Secure bcrypt password storage
- **Token Validation**: Automatic session management and expiry handling
- **Protected Endpoints**: All sensitive operations require authentication

##  Tech Stack

### **Backend**
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: Database ORM for data management
- **JWT**: JSON Web Tokens for authentication
- **Pydantic**: Data validation and serialization
- **Passlib**: Password hashing and verification
- **SQLite**: Default database (easily configurable to PostgreSQL)

### **Frontend**
- **Streamlit**: Interactive web application framework
- **Pandas**: Data manipulation and analysis
- **Requests**: HTTP client for API communication

## 📁 Project Structure

```
bookmemovie/
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── menv/                    # Virtual environment (gitignored)
└── app/
    ├── .env                 # Environment variables (gitignored)
    ├── config.py            # Configuration management
    ├── database.py          # Database connection and setup
    ├── main.py              # FastAPI application entry point
    ├── dashboard.py         # Streamlit frontend application
    ├── core/
    │   └── auth.py          # Authentication and authorization
    ├── models/
    │   ├── user.py          # User model
    │   ├── movie.py         # Movie model
    │   ├── event.py         # Event model
    │   └── seat.py          # Seat model
    ├── routes/
    │   ├── auth.py          # Authentication routes
    │   ├── seat.py          # Seat booking routes
    │   └── admin.py         # Admin management routes
    └── schemas/
        ├── auth.py          # Authentication schemas
        ├── seat.py          # Seat booking schemas
        └── admin.py         # Admin schemas
```

##  Installation & Setup

### **Prerequisites**
- Python 3.8+
- pip (Python package manager)
- Git

### **1. Clone the Repository**
```bash
git clone <your-repo-url>
cd bookmemovie
```

### **2. Create Virtual Environment**
```bash
python -m venv menv
source menv/bin/activate  # On Windows: menv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt```

### **4. Environment Configuration**
```bash
# Copy the environment template
cp .env.example app/.env

# Generate a secure SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Edit app/.env with your configuration
```

### **5. Required Environment Variables**
Edit `app/.env` with your values:

```bash
# REQUIRED - Use the generated secret key
SECRET_KEY=your-generated-secret-key-here

# OPTIONAL - Application settings
DATABASE_URL=sqlite:///./movie_ticketing.db
DEBUG=true
BASE_URL=http://localhost:8000
```

##  Running the Application

### **Start the Backend API**
```bash
cd app
uvicorn main:app --reload
```
The API will be available at: `http://localhost:8000`

### **Start the Frontend Dashboard**
```bash
# In a new terminal
cd bookmemovie
streamlit run app/dashboard.py
```
The dashboard will be available at: `http://localhost:8501`

### **Access API Documentation**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

##  Configuration

### **Database Configuration**
```bash
# SQLite (Default - for development)
DATABASE_URL=sqlite:///./movie_ticketing.db


### **Environment-Specific Settings**
```bash
# Development
DEBUG=true
BASE_URL=http://localhost:8000

# Production
DEBUG=false
BASE_URL=https://your-domain.com
```

##  Usage

### **First-Time Setup**
1. **Start both applications** (backend and frontend)
2. **Open the dashboard** at `http://localhost:8501`
3. **Go to "Admin Setup" tab**
4. **Create admin user** with your chosen credentials
5. **Login** with your admin credentials

### **Admin Operations**
1. **Login** as admin
2. **Add movies** to the catalog
3. **Schedule events** (showtimes) for movies
4. **Monitor bookings** and system analytics

### **Customer Operations**
1. **Register** or **login** as a customer
2. **Browse available movies** and showtimes
3. **Select seats** using the interactive seat map
4. **Book tickets** and confirm payment
5. **Manage bookings** (cancel if needed)

##  API Endpoints

### **Authentication**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/create-admin` - Create admin user

### **Customer Operations**
- `GET /api/events` - List all events
- `GET /api/events/{event_id}/seats` - Get seats for event
- `POST /api/book-seats` - Book seats
- `POST /api/confirm-payment` - Confirm booking payment
- `POST /api/cancel-booking` - Cancel booking

### **Admin Operations**
- `GET /api/admin/movies` - List all movies
- `POST /api/admin/movies` - Create movie
- `PUT /api/admin/movies/{movie_id}` - Update movie
- `DELETE /api/admin/movies/{movie_id}` - Delete movie
- `GET /api/admin/events` - List all events (admin view)
- `POST /api/admin/events` - Create event
- `PUT /api/admin/events/{event_id}` - Update event
- `DELETE /api/admin/events/{event_id}` - Delete event

## 🔐 Security

### **Authentication Flow**
1. **User registers/logs in** → Receives JWT token
2. **Token included in requests** → `Authorization: Bearer <token>`
3. **Server validates token** → Grants/denies access
4. **Token expires** → User must login again

### **Role-Based Access**
- **Users**: Can browse movies, book seats, manage their bookings
- **Admins**: Full system access including movie/event management

### **Password Security**
- **Bcrypt hashing** for password storage



##  Testing

### **Test Admin Flow**
```bash
# 1. Create admin via API
curl -X POST "http://localhost:8000/api/auth/create-admin" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "secure123", "full_name": "Test Admin"}'

# 2. Login and get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "secure123"}'

# 3. Use token for authenticated requests
curl -X GET "http://localhost:8000/api/admin/movies" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

