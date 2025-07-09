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
    1. **Setup Admin** (first time): Use the "Admin Setup" tab to create admin user
    2. **Login**: POST `/api/auth/login` with your credentials
    3. **Authorize**: Click the 🔒 "Authorize" button and enter: `Bearer YOUR_TOKEN`
    4. **Use protected endpoints**: Now you can access authenticated routes
    
    ### Setup Process:
    1. Create admin user via frontend or API
    2. Login with your admin credentials
    3. Start managing movies and events
    
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
        "setup": "Create admin user first via frontend or POST /api/auth/create-admin"
    }

@app.get("/health", tags=["📋 System Info"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": config.app_name,
        "version": config.app_version,
        "database": "connected" if engine else "disconnected",
        "config_valid": True
    }
