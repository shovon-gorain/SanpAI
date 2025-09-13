import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DATABASE = 'database.db'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    API_KEY = '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'  # Replace with your actual API key