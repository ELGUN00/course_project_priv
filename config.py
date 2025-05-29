import os 
class Config:
    """Base configuration for the app."""
    # Secret key for session management and JWT signing
    SECRET_KEY = os.getenv('SECRET_KEY', 'dune')  
    # JWT token expiration time (in seconds)
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:12@pgbouncer:6432/test')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # To disable modification tracking (to save memory)
    
    # OAuth keys for Google and Apple (can be set in environment variables)
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    APPLE_CLIENT_ID = os.getenv('APPLE_CLIENT_ID')
    APPLE_CLIENT_SECRET = os.getenv('APPLE_CLIENT_SECRET')
