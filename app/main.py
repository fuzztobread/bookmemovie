from fastapi import FastAPI
from database import engine, Base
from routes.seat import router as seats_router
from routes.admin import router as admin_router
from routes.auth import router as auth_router
from config import get_config

# Import ALL models explicitly so SQLAlchemy knows about them
from models.movie import Movie     # noqa: F401
from models.event import Event     # noqa: F401
from models.seat import Seat       # noqa: F401
from models.user import User       # noqa: F401

# Get config once - this validates everything at startup
config = get_config()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=config.app_name,
    description=f"""
    ## Secure Movie Ticketing System with JWT Authentication
    
    **Version:** {config.app_version}
    
    ### How to use:
    1. **Create Admin** (one-time): POST `/api/auth/create-admin`
    2. **Login**: POST `/api/auth/login` with your credentials
    3. **Authorize**: Click the 🔒 "Authorize" button and enter: `Bearer YOUR_TOKEN`
    4. **Use protected endpoints**: Now you can access authenticated routes
    
    ### Admin Credentials:
    - Email: `{config.admin_email}`
    - Password: `{config.admin_password}`
    
    ### Configuration Status:
    - Debug Mode: `{config.debug}`
    - Database: `{config.database_url}`
    - Token Expiry: `{config.access_token_expire_minutes} minutes`
    - Seat Lock Duration: `{config.seat_lock_duration_minutes} minutes`
    """,
    version=config.app_version,
    debug=config.debug
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["🔐 Authentication"])
app.include_router(seats_router, prefix="/api", tags=["🎫 Seat Booking"])
app.include_router(admin_router, prefix="/api/admin", tags=["👨‍💼 Admin Panel"])

@app.get("/", tags=["📋 System Info"])
def read_root():
    return {
        "message": f"{config.app_name} is running! 🎬", 
        "version": config.app_version,
        "auth": "JWT enabled 🔒",
        "docs": "Visit /docs to test the API with authentication 📖",
        "admin_email": config.admin_email,
        "setup": "Create admin first: POST /api/auth/create-admin"
    }


